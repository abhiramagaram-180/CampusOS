"""genie_client.py - real Databricks Genie + SQL execution client."""

from __future__ import annotations

import time
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
	from databricks.sdk import WorkspaceClient
	from databricks.sdk.errors import DatabricksError
	HAS_DATABRICKS_SDK = True
except ImportError:
	HAS_DATABRICKS_SDK = False


def _get_client():
	if HAS_DATABRICKS_SDK:
		host = os.getenv("DATABRICKS_HOST", "")
		token = os.getenv("DATABRICKS_TOKEN", "")
		if not host or not token:
			raise RuntimeError(
				"Set DATABRICKS_HOST and DATABRICKS_TOKEN env vars."
			)
		return WorkspaceClient(host=host, token=token)
	raise RuntimeError("Install databricks-sdk.")


def ask_genie(question, space_id, warehouse_id, conversation_id=None, timeout=120, poll_interval=2.0):
	from config import GenieAnswer

	if not space_id:
		return GenieAnswer(
			answer_text="Genie Space ID not configured.",
			data=None, sql=None, conversation_id=None,
			error="Set CAMPUSOS_PLACEMENT_SPACE_ID.",
		)

	client = _get_client()
	start = time.time()
	current_conv_id = conversation_id

	try:
		# Start or continue conversation
		if current_conv_id:
			message = client.genie.start_conversation(
				space_id=space_id,
				conversation_id=current_conv_id,
				content=question,
			)
		else:
			result = client.genie.start_conversation(
				space_id=space_id,
				content=question,
			)
			message = result
			current_conv_id = message.conversation_id

		# Poll for response
		attachment = None
		while time.time() - start < timeout:
			time.sleep(poll_interval)
			msg = client.genie.get_message(
				space_id=space_id,
				conversation_id=current_conv_id,
				message_id=message.message_id,
			)
			if hasattr(msg, "attachments") and msg.attachments:
				attachment = msg.attachments[0]
				break
			if hasattr(msg, "status") and msg.status in ("COMPLETED", "FAILED", "CANCELLED"):
				break

		# Timeout check
		if time.time() - start > timeout:
			return GenieAnswer(
				answer_text="Request timed out. Try again.",
				data=None, sql=None, conversation_id=current_conv_id,
				error="timeout",
			)

		# Extract answer
		answer_text = ""
		data = None
		sql_text = None

		if attachment:
			if hasattr(attachment, "text"):
				answer_text = attachment.text or ""

			if hasattr(attachment, "query"):
				sql_text = attachment.query

			# Try to get result data
			try:
				if hasattr(attachment, "query_id"):
					query_result = client.sql.get_query_results(
						query_id=attachment.query_id,
					)
					try:
						import polars as pl
						data = pl.DataFrame(query_result.data)
					except Exception:
						data = None
			except Exception:
				data = None

			# Fallback: run SQL if we have it but no data
			if sql_text and data is None:
				try:
					data = execute_sql(sql_text, warehouse_id)
				except Exception:
					pass

			if not answer_text:
				answer_text = "Query executed." if sql_text else "No response."

			return GenieAnswer(
				answer_text=answer_text,
				data=data,
				sql=sql_text,
				conversation_id=current_conv_id,
				error=None,
			)

		# No attachment
		return GenieAnswer(
			answer_text=answer_text or "No response from Genie.",
			data=None, sql=None, conversation_id=current_conv_id,
			error=None,
		)

	except DatabricksError as e:
		msg = getattr(e, "message", None) or str(e)
		return GenieAnswer(
			answer_text=f"Error: {msg}",
			data=None, sql=None, conversation_id=current_conv_id,
			error=str(e),
		)
	except Exception as e:
		return GenieAnswer(
			answer_text=f"Error: {e}",
			data=None, sql=None, conversation_id=current_conv_id,
			error=str(e),
		)


def execute_sql(statement: str, warehouse_id: str, timeout: int = 120):
	"""Execute INSERT/UPDATE/DDL via Databricks SQL API."""
	if not warehouse_id:
		raise RuntimeError("Warehouse ID not set.")

	client = _get_client()
	start = time.time()

	try:
		resp = client.sql.create_statement(
			warehouse_id=warehouse_id,
			statement=statement,
		)
		statement_id = resp.statement_id

		while time.time() - start < timeout:
			time.sleep(1.5)
			status = client.sql.get_statement(statement_id)

			if status.status in ("SUCCEEDED", "COMPLETED"):
				if hasattr(status, "result") and status.result:
					try:
						import polars as pl
						return pl.DataFrame(status.result.data_array)
					except Exception:
						if hasattr(status.result, "data_array"):
							return status.result.data_array
						return status.result
				return None

			if status.status in ("FAILED", "CANCELED", "CLOSED"):
				raise RuntimeError(
					f"SQL failed: {getattr(status, 'error', 'unknown')}"
				)

	except DatabricksError as e:
		raise RuntimeError(f"Databricks error: {getattr(e, 'message', str(e))}")
	except Exception as e:
		raise RuntimeError(f"SQL error: {e}")
