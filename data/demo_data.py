simulations = {
    "use_case_billing_and_banking": {
        "use_case": "Billing & Banking",
        "sub_use_case": "Full Info: Retrieve Bills, Check Balance, Update Account",
        "steps": [
            {
                "step_name": "User Authentication",
                "trigger_event": "User tries to access account, provides user_id/password",
                "expected_functions": [
                    {
                        "function_name": "authenticate_user",
                        "input_passed": {
                            "user_id": "string",
                            "password": "string"
                        }
                    }
                ],
                "expected_response": "Acknowledgment of successful or failed login."
            },
            {
                "step_name": "Retrieve Billing Information",
                "trigger_event": "User mentions 'April 2024' or wants monthly bills",
                "expected_functions": [
                    {
                        "function_name": "validate_bill_request",
                        "input_passed": {
                            "user_id": "string",
                            "month": "string",
                            "year": "integer"
                        }
                    },
                    {
                        "function_name": "get_billing_statements",
                        "input_passed": {
                            "user_id": "string",
                            "month": "string",
                            "year": "integer"
                        }
                    }
                ],
                "expected_response": (
                    "Here are your bills for April 2024. Bill 1: $120.50 on 2024-04-05 - Paid. "
                    "Bill 2: $80.75 on 2024-04-20 - Due."
                )
            },
            {
                "step_name": "Check Balance",
                "trigger_event": "User asks about negative or current balance",
                "expected_functions": [
                    {
                        "function_name": "check_balance",
                        "input_passed": {
                            "user_id": "string"
                        }
                    }
                ],
                "expected_response": "Displays the user's account balance (positive or negative)."
            },
            {
                "step_name": "Update Bank Info",
                "trigger_event": "User wants to change bank account or routing info",
                "expected_functions": [
                    {
                        "function_name": "update_bank_info",
                        "input_passed": {
                            "user_id": "string",
                            "new_account_number": "string"
                        }
                    }
                ],
                "expected_response": (
                    "Confirmation that the user's bank info is updated successfully."
                )
            }
        ]
    }
}

conversations = {
    # FULLY VALID conversation - matches the expected steps exactly
    "conversation_fully_valid": [
        {
            "user_query": "hello",
            "actual_function_calls": [],
            "response": "Hi! How can I help you with your account today?"
        },
        {
            "user_query": "i want to see bills for april 2024",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userA1",
                        "password": "some_hashed_pass"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                },
                {
                    "function_name": "validate_bill_request",
                    "input_passed": {"user_id": "userA1", "month": "April", "year": 2024},
                    "output_passed": {"is_valid": True, "error_messages": []}
                },
                {
                    "function_name": "get_billing_statements",
                    "input_passed": {"user_id": "userA1", "month": "April", "year": 2024},
                    "output_passed": {
                        "bills": [
                            {"date": "2024-04-05", "amount": 120.50, "status": "Paid"},
                            {"date": "2024-04-20", "amount": 80.75, "status": "Due"}
                        ]
                    }
                }
            ],
            "response": (
                "Here are your bills for April 2024. Bill 1: $120.50 on 2024-04-05 - Paid. "
                "Bill 2: $80.75 on 2024-04-20 - Due."
            )
        },
        {
            "user_query": "Ok thanks. do I have negative balance or some?",
            "actual_function_calls": [
                {
                    "function_name": "check_balance",
                    "input_passed": {"user_id": "userA1"},
                    "output_passed": {
                        "balance": 250.00,
                        "currency": "USD"
                    }
                }
            ],
            "response": (
                "Your account balance is $250.00. You do not have a negative balance. "
                "Is there anything else I can help you with?"
            )
        }
    ],

    # PARTIALLY VALID conversation - some steps match, some are missing or irrelevant
    "conversation_partially_valid": [
        {
            "user_query": "hey agent i want to update my bank info??",
            "actual_function_calls": [],
            "response": "Certainly! May I have your user ID first?"
        },
        {
            "user_query": "my user is userB2",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userB2",
                        "password": "unknown"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                },
                {
                    # 'validate_bill_request' is irrelevant here but was called anyway
                    "function_name": "validate_bill_request",
                    "input_passed": {"user_id": "userB2", "month": "", "year": 0},
                    "output_passed": {"is_valid": False, "error_messages": ["Missing month/year"]}
                }
            ],
            "response": (
                "I see you've provided partial info for a bill request, but let's focus on updating bank info. "
                "Authenticated as userB2. Please provide your new bank details."
            )
        },
        {
            "user_query": "my new bank account 9999999. just do it pls??",
            "actual_function_calls": [
                {
                    "function_name": "update_bank_info",
                    "input_passed": {
                        "user_id": "userB2",
                        "new_account_number": "9999999"
                    },
                    "output_passed": {
                        "update_status": "Success"
                    }
                }
            ],
            "response": (
                "Your bank info has been updated to account #9999999. Anything else?"
            )
        },
        {
            # The user asks about negative balance but no function is actually called
            "user_query": "just do i have negative balance??",
            "actual_function_calls": [],
            "response": (
                "I don't see any function call for checking your balance. "
                "Would you like me to check it?"
            )
        }
    ],

    # NOT MATCHING conversation - random or irrelevant queries, no correct function calls
    "conversation_not_matching": [
        {
            "user_query": "hello i want a pizza deliver??",
            "actual_function_calls": [],
            "response": (
                "I'm sorry, I can only assist with banking requests. Could you clarify your banking need?"
            )
        },
        {
            "user_query": "um maybe i check something about april 2024 but not sure??",
            "actual_function_calls": [],
            "response": "I didn't see any function calls or steps to retrieve bills yet."
        },
        {
            "user_query": "nvm bye",
            "actual_function_calls": [],
            "response": "Alright, have a nice day!"
        }
    ],

    # ANOTHER VALID conversation, but shorter
    "conversation_short_valid": [
        {
            "user_query": "hi i want check my balance real quick",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userD4",
                        "password": "random_pass"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                },
                {
                    "function_name": "check_balance",
                    "input_passed": {"user_id": "userD4"},
                    "output_passed": {
                        "balance": 100.00,
                        "currency": "USD"
                    }
                }
            ],
            "response": "Your account balance is $100.00."
        },
        {
            "user_query": "thankss laters",
            "actual_function_calls": [],
            "response": "Thank you! Have a good day."
        }
    ]
}
