"""Set BESPOKE_API_KEY; optionally set BESPOKE_LABS_BASE_URL to your gateway."""

from bespokelabs import nimble

with nimble.Nimble() as client:
    response = client.system_one(
        state="Please refund the duplicate payment.",
        questions={
            "refund": {"type": "noul", "instructions": "Does the customer request a refund?"},
            "department": {
                "type": "choice",
                "instructions": "Which department should handle this?",
                "criteria": {"billing": "Payments and refunds", "technical": "Software bugs"},
            },
        },
    )
    print(response.nouls["refund"].noul)
    print(response.choices["department"].choice)
