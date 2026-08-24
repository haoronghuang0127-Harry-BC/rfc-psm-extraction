# JSON Schema used by Research extraction and combination
FSM_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "states": {
            "type": "array",
            "items": {
                "type": "string",
                "minLength": 1,
            },
        },
        "transitions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "event": {
                        "type": "string",
                    },
                    "action": {
                        "type": "string",
                    },
                    "to": {
                        "type": "string",
                        "minLength": 1,
                    },
                },
                "required": [
                    "from",
                    "event",
                    "action",
                    "to",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "states",
        "transitions",
    ],
    "additionalProperties": False,
}