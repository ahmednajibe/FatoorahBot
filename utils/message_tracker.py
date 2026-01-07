"""
Message Tracking Utility
Helper functions for tracking related messages
"""


async def add_related_message(state, message_id: int):
    """Add a message ID to the related_messages list."""
    data = await state.get_data()
    related_messages = data.get("related_messages", [])
    related_messages.append(message_id)
    await state.update_data(related_messages=related_messages)
