simulations = {
    # -------------------------------------------------------------------
    # 1) ADVANCED BILLING & PARTIAL PAYMENT SCENARIO
    # -------------------------------------------------------------------
    "use_case_advanced_billing_partial_payment": {
        "use_case": "Billing & Banking",
        "sub_use_case": "Retrieve Bills, Partial Payments, Late Fee Calculation",
        "steps": [
            {
                "step_name": "User Authentication",
                "trigger_event": "User tries to discuss or pay bills, provides user_id/password",
                "expected_functions": [
                    {
                        "function_name": "authenticate_user",
                        "input_passed": {
                            "user_id": "string",
                            "password": "string"
                        }
                    }
                ],
                "expected_response": "User is successfully or unsuccessfully authenticated."
            },
            {
                "step_name": "Retrieve Outstanding Bills",
                "trigger_event": "User mentions a specific month/year or says 'I owe money?'",
                "expected_functions": [
                    {
                        "function_name": "get_outstanding_bills",
                        "input_passed": {
                            "user_id": "string"
                        }
                    }
                ],
                "expected_response": (
                    "Displays the user's outstanding bills with due dates and total due amounts."
                )
            },
            {
                "step_name": "Process Partial Payment",
                "trigger_event": (
                    "User states they can only pay part of the total, or mentions a certain "
                    "amount they want to pay."
                ),
                "expected_functions": [
                    {
                        "function_name": "process_partial_payment",
                        "input_passed": {
                            "user_id": "string",
                            "payment_amount": "number"
                        }
                    }
                ],
                "expected_response": (
                    "Acknowledges the partial payment and shows the new remaining balance."
                )
            },
            {
                "step_name": "Calculate Late Fee",
                "trigger_event": (
                    "User is past due date or has partial payment that might incur a late fee."
                ),
                "expected_functions": [
                    {
                        "function_name": "calculate_late_fee",
                        "input_passed": {
                            "user_id": "string"
                        }
                    }
                ],
                "expected_response": (
                    "Displays the late fee applied (if any) and the updated total amount."
                )
            }
        ]
    },

    # -------------------------------------------------------------------
    # 2) CROSS-LANGUAGE SUPPORT & CONFUSED USER
    # -------------------------------------------------------------------
    "use_case_cross_language_support": {
        "use_case": "General Account Help",
        "sub_use_case": "User with limited English, partial Spanish, unclear queries",
        "steps": [
            {
                "step_name": "User Authentication",
                "trigger_event": (
                    "User tries to get help in mixed English/Spanish, attempts to provide user_id/password."
                ),
                "expected_functions": [
                    {
                        "function_name": "authenticate_user",
                        "input_passed": {
                            "user_id": "string",
                            "password": "string"
                        }
                    }
                ],
                "expected_response": (
                    "Acknowledgment of successful or failed login, possibly clarifying user input in simpler terms."
                )
            },
            {
                "step_name": "Identify Help Topic",
                "trigger_event": (
                    "User vaguely references account, billing, or plan in broken English or Spanish phrases."
                ),
                "expected_functions": [
                    {
                        "function_name": "detect_user_intent",
                        "input_passed": {
                            "query_text": "string"
                        }
                    }
                ],
                "expected_response": (
                    "Chatbot clarifies or restates the problem in simpler English/Spanish, prompting user to confirm the topic."
                )
            },
            {
                "step_name": "Resolve or Transfer",
                "trigger_event": (
                    "User clarifies they need help with billing or plan. The system either resolves the issue or routes to a specialized function."
                ),
                "expected_functions": [
                    {
                        "function_name": "resolve_billing_inquiry",
                        "input_passed": {
                            "user_id": "string",
                            "month": "string",
                            "year": "integer"
                        }
                    }
                ],
                "expected_response": (
                    "Information on the relevant topic (bill, plan, etc.) or a prompt to confirm details in both languages."
                )
            }
        ]
    },

    # -------------------------------------------------------------------
    # 3) ROAMING & COVERAGE TROUBLESHOOTING (Older Landline + Confused Phrases)
    # -------------------------------------------------------------------
    "use_case_roaming_coverage_landline": {
        "use_case": "Network & Coverage",
        "sub_use_case": "Roaming Activation, Coverage Check, Landline Confusion",
        "steps": [
            {
                "step_name": "User Authentication",
                "trigger_event": "User tries to activate roaming or check coverage, provides credentials",
                "expected_functions": [
                    {
                        "function_name": "authenticate_user",
                        "input_passed": {
                            "user_id": "string",
                            "password": "string"
                        }
                    }
                ],
                "expected_response": "User is successfully or unsuccessfully authenticated."
            },
            {
                "step_name": "Check Roaming Eligibility",
                "trigger_event": (
                    "User mentions traveling abroad or asks if calls will work outside local region."
                ),
                "expected_functions": [
                    {
                        "function_name": "check_roaming_eligibility",
                        "input_passed": {
                            "user_id": "string"
                        }
                    }
                ],
                "expected_response": "Indicates whether the user’s plan supports roaming or not."
            },
            {
                "step_name": "Activate Roaming or Coverage",
                "trigger_event": (
                    "User wants to enable roaming or verify coverage in a certain country/region."
                ),
                "expected_functions": [
                    {
                        "function_name": "activate_roaming",
                        "input_passed": {
                            "user_id": "string",
                            "country_code": "string"
                        }
                    },
                    {
                        "function_name": "check_coverage_map",
                        "input_passed": {
                            "country_code": "string"
                        }
                    }
                ],
                "expected_response": (
                    "Confirmation that roaming is activated, plus coverage details for the region."
                )
            },
            {
                "step_name": "Landline Confusion Resolution",
                "trigger_event": (
                    "User references an old landline phone or wonders if it needs roaming."
                ),
                "expected_functions": [
                    {
                        "function_name": "explain_landline_usage",
                        "input_passed": {
                            "user_id": "string"
                        }
                    }
                ],
                "expected_response": (
                    "Clarifies that landlines do not require roaming and offers additional help if needed."
                )
            }
        ]
    }
}


conversations = {
    # -------------------------------------------------------------------
    # ADVANCED BILLING & PARTIAL PAYMENT: FULLY VALID
    # -------------------------------------------------------------------
    "conversation_fully_valid_advanced_billing": [
        {
            "user_query": "Hello? Eh... me pay some money for the phone I owe. Mi ID es userX1, pass is passX1",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userX1",
                        "password": "passX1"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                }
            ],
            "response": "Okay, userX1 authenticated. Let's see your outstanding bills. One moment."
        },
        {
            "user_query": "Yes, yes. I'm older lady, can't pay all. Show me the bills, por favor.",
            "actual_function_calls": [
                {
                    "function_name": "get_outstanding_bills",
                    "input_passed": {
                        "user_id": "userX1"
                    },
                    "output_passed": {
                        "bills": [
                            {
                                "month": "May",
                                "year": 2024,
                                "amount_due": 200.00,
                                "due_date": "2024-05-25"
                            }
                        ]
                    }
                }
            ],
            "response": "Your total due for May 2024 is $200.00, due by May 25, 2024."
        },
        {
            "user_query": "Oh, I have only 100. I'll pay half. Then rest next week, ok?",
            "actual_function_calls": [
                {
                    "function_name": "process_partial_payment",
                    "input_passed": {
                        "user_id": "userX1",
                        "payment_amount": 100.00
                    },
                    "output_passed": {
                        "new_balance": 100.00
                    }
                }
            ],
            "response": "We received your partial payment of $100. Your new balance is $100."
        },
        {
            "user_query": "But am I get penalty now? I pay late next week maybe.",
            "actual_function_calls": [
                {
                    "function_name": "calculate_late_fee",
                    "input_passed": {
                        "user_id": "userX1"
                    },
                    "output_passed": {
                        "late_fee": 10.00
                    }
                }
            ],
            "response": "A late fee of $10 will apply after your due date. Your total after May 25 will be $110."
        }
    ],

    # -------------------------------------------------------------------
    # ADVANCED BILLING & PARTIAL PAYMENT: PARTIALLY VALID
    # (User mis-steps, missing function call, etc.)
    # -------------------------------------------------------------------
    "conversation_partially_valid_advanced_billing": [
        {
            # User never provides password, tries to see bills
            "user_query": "I want see how much I owe. My ID userX2. No password though, sorry.",
            "actual_function_calls": [
                {
                    # Attempt to retrieve bills without authentication
                    "function_name": "get_outstanding_bills",
                    "input_passed": {
                        "user_id": "userX2"
                    },
                    "output_passed": {
                        "bills": []
                    }
                }
            ],
            "response": (
                "I'm sorry, we need to authenticate you first before retrieving your bills. "
                "Please provide your password."
            )
        },
        {
            "user_query": "Ok, pass is passX2. Now hurry up, I pay 50 only!",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userX2",
                        "password": "passX2"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                }
            ],
            "response": (
                "You're authenticated. Let's fetch your outstanding bills."
            )
        },
        {
            # The user tries to pay partial without the system actually retrieving the bills
            "user_query": "Yes. Bill me 50. Done.",
            "actual_function_calls": [
                {
                    "function_name": "process_partial_payment",
                    "input_passed": {
                        "user_id": "userX2",
                        "payment_amount": 50.00
                    },
                    "output_passed": {
                        "new_balance": 150.00
                    }
                }
            ],
            "response": (
                "Partial payment processed for $50. However, we haven't shown you the exact bill details. "
                "Your estimated remaining balance is $150. Do you want to see your full bill?"
            )
        }
    ],

    # -------------------------------------------------------------------
    # ADVANCED BILLING & PARTIAL PAYMENT: NOT MATCHING
    # (User is extremely off-topic or references something else)
    # -------------------------------------------------------------------
    "conversation_not_matching_advanced_billing": [
        {
            "user_query": "I want to talk about pizza again... you got a coupon?",
            "actual_function_calls": [],
            "response": (
                "We handle telecommunications billing and banking. "
                "I'm afraid we don't have pizza coupons."
            )
        },
        {
            "user_query": "Ok then, do you rent VHS tapes? I'm old. Need a movie for free?",
            "actual_function_calls": [],
            "response": "Sorry, we don't handle VHS rentals. Can I help with your phone or internet bill instead?"
        },
        {
            "user_query": "No, I'm done. Bye.",
            "actual_function_calls": [],
            "response": "Have a good day!"
        }
    ],

    # -------------------------------------------------------------------
    # ADVANCED BILLING & PARTIAL PAYMENT: SHORT VALID
    # -------------------------------------------------------------------
    "conversation_short_valid_advanced_billing": [
        {
            "user_query": "I must pay quickly. userX3 passX3. Only 30 bucks I have.",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userX3",
                        "password": "passX3"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                },
                {
                    "function_name": "process_partial_payment",
                    "input_passed": {
                        "user_id": "userX3",
                        "payment_amount": 30.00
                    },
                    "output_passed": {
                        "new_balance": 170.00
                    }
                }
            ],
            "response": (
                "You're authenticated. Partial payment of $30 accepted. "
                "Your remaining balance is $170. Thank you."
            )
        }
    ],

    # -------------------------------------------------------------------
    # CROSS-LANGUAGE SUPPORT: FULLY VALID
    # (User speaks broken English/Spanish, system interprets and resolves)
    # -------------------------------------------------------------------
    "conversation_fully_valid_cross_language": [
        {
            "user_query": "Hola? I have problema with bill. userLang1, passLang1?",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userLang1",
                        "password": "passLang1"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                }
            ],
            "response": (
                "Hola, you're authenticated! Could you describe your billing issue in English or Spanish?"
            )
        },
        {
            "user_query": "Quiero ver la factura from April. No comprendo how much I pay?",
            "actual_function_calls": [
                {
                    "function_name": "detect_user_intent",
                    "input_passed": {
                        "query_text": "Quiero ver la factura from April. No comprendo how much I pay?"
                    },
                    "output_passed": {
                        "intent": "billing_inquiry"
                    }
                },
                {
                    "function_name": "resolve_billing_inquiry",
                    "input_passed": {
                        "user_id": "userLang1",
                        "month": "April",
                        "year": 2025
                    },
                    "output_passed": {
                        "amount_due": 75.00,
                        "due_date": "2025-04-30"
                    }
                }
            ],
            "response": (
                "Para April 2025, you owe $75.00 due by April 30. ¿Desea pagar ahora?"
            )
        }
    ],

    # -------------------------------------------------------------------
    # CROSS-LANGUAGE SUPPORT: PARTIALLY VALID
    # (User changes topic mid-conversation, no final resolution)
    # -------------------------------------------------------------------
    "conversation_partially_valid_cross_language": [
        {
            "user_query": "Buenos días, no hablo English good. My ID is userLang2.",
            "actual_function_calls": [],
            "response": (
                "Hola, userLang2. Please provide your password to authenticate."
            )
        },
        {
            "user_query": "Password? Eh, not sure. My memory is bad. Maybe passLang2.",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userLang2",
                        "password": "passLang2"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                }
            ],
            "response": "You're logged in. How may I help you?"
        },
        {
            # User never clarifies the help topic
            "user_query": "I forget... I'm old. Something about plan or maybe pizza. Quien sabe.",
            "actual_function_calls": [],
            "response": (
                "I'm not sure what you mean. Could you clarify if you want help with your plan?"
            )
        }
    ],

    # -------------------------------------------------------------------
    # CROSS-LANGUAGE SUPPORT: NOT MATCHING
    # (User insists on non-telecom queries in Spanish/English mix)
    # -------------------------------------------------------------------
    "conversation_not_matching_cross_language": [
        {
            "user_query": "Hola, can you order me un taxi?",
            "actual_function_calls": [],
            "response": (
                "Lo siento, I can only help with account or billing issues. "
                "Would you like account support?"
            )
        },
        {
            "user_query": "No, just necesito un taxi. Adiós.",
            "actual_function_calls": [],
            "response": "Ok, bye. Have a nice day!"
        }
    ],

    # -------------------------------------------------------------------
    # CROSS-LANGUAGE SUPPORT: SHORT VALID
    # -------------------------------------------------------------------
    "conversation_short_valid_cross_language": [
        {
            "user_query": "¿Puedo ver mi balance? userLang3, passLang3.",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userLang3",
                        "password": "passLang3"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                },
                {
                    "function_name": "detect_user_intent",
                    "input_passed": {
                        "query_text": "¿Puedo ver mi balance?"
                    },
                    "output_passed": {
                        "intent": "check_balance"
                    }
                },
                {
                    "function_name": "resolve_billing_inquiry",
                    "input_passed": {
                        "user_id": "userLang3",
                        "month": "",
                        "year": 0
                    },
                    "output_passed": {
                        "amount_due": 0.00,
                        "due_date": None,
                        "balance": 45.00  # user credit
                    }
                }
            ],
            "response": (
                "Su balance actual es $45.00 a favor. ¿Alguna otra cosa?"
            )
        }
    ],

    # -------------------------------------------------------------------
    # ROAMING & COVERAGE TROUBLESHOOTING: FULLY VALID
    # (User references older phone + confusion about landline)
    # -------------------------------------------------------------------
    "conversation_fully_valid_roaming_coverage": [
        {
            "user_query": "Hi, I’m traveling. My ID userR1. passR1. Will my old phone line need roam?",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userR1",
                        "password": "passR1"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                }
            ],
            "response": "You've been authenticated. Let’s check your roaming eligibility."
        },
        {
            "user_query": "Yes, I'm going to Canada. Also I have an old landline phone. Does that matter?",
            "actual_function_calls": [
                {
                    "function_name": "check_roaming_eligibility",
                    "input_passed": {
                        "user_id": "userR1"
                    },
                    "output_passed": {
                        "is_roaming_supported": True,
                        "error_messages": []
                    }
                },
                {
                    "function_name": "activate_roaming",
                    "input_passed": {
                        "user_id": "userR1",
                        "country_code": "CA"
                    },
                    "output_passed": {
                        "roaming_status": "Activated"
                    }
                },
                {
                    "function_name": "check_coverage_map",
                    "input_passed": {
                        "country_code": "CA"
                    },
                    "output_passed": {
                        "coverage_level": "4G/LTE in major cities"
                    }
                }
            ],
            "response": (
                "Your roaming is activated for Canada. Coverage is mostly 4G/LTE. "
                "Landlines don't need roaming, so your old phone at home isn't affected."
            )
        },
        {
            "user_query": "Oh good. So I can call from Canada using my mobile. Thank you!",
            "actual_function_calls": [
                {
                    "function_name": "explain_landline_usage",
                    "input_passed": {
                        "user_id": "userR1"
                    },
                    "output_passed": {
                        "explanation": "Landlines at home use local phone lines. No roaming required."
                    }
                }
            ],
            "response": (
                "Exactly. Your landline at home doesn't need roaming. Anything else?"
            )
        }
    ],

    # -------------------------------------------------------------------
    # ROAMING & COVERAGE TROUBLESHOOTING: PARTIALLY VALID
    # (User forgets to mention destination, tries to activate roaming for landline, etc.)
    # -------------------------------------------------------------------
    "conversation_partially_valid_roaming_coverage": [
        {
            "user_query": "Hello. userR2 passR2. I want roaming for my big black phone at home.",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userR2",
                        "password": "passR2"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                }
            ],
            "response": (
                "Authenticated. We need to confirm if you have a mobile device or a landline."
            )
        },
        {
            "user_query": "It's an old phone with a cord in kitchen. Turn on roam now!",
            "actual_function_calls": [
                {
                    "function_name": "activate_roaming",
                    "input_passed": {
                        "user_id": "userR2",
                        "country_code": ""  # Not provided
                    },
                    "output_passed": {
                        "roaming_status": "Error - Device not supported"
                    }
                }
            ],
            "response": (
                "It seems you're trying to enable roaming on a landline, which isn't supported. "
                "Do you have a mobile device you want roaming for?"
            )
        }
    ],

    # -------------------------------------------------------------------
    # ROAMING & COVERAGE TROUBLESHOOTING: NOT MATCHING
    # -------------------------------------------------------------------
    "conversation_not_matching_roaming_coverage": [
        {
            "user_query": "I need coverage for my imaginary spaceship phone, do you do that?",
            "actual_function_calls": [],
            "response": (
                "We only handle terrestrial mobile and landline coverage. "
                "I'm afraid we can't help with a spaceship phone."
            )
        },
        {
            "user_query": "Ok, guess I'll figure it out. Bye.",
            "actual_function_calls": [],
            "response": "Take care!"
        }
    ],

    # -------------------------------------------------------------------
    # ROAMING & COVERAGE TROUBLESHOOTING: SHORT VALID
    # -------------------------------------------------------------------
    "conversation_short_valid_roaming_coverage": [
        {
            "user_query": "Going to Mexico. userR3 passR3. Turn on roam plz.",
            "actual_function_calls": [
                {
                    "function_name": "authenticate_user",
                    "input_passed": {
                        "user_id": "userR3",
                        "password": "passR3"
                    },
                    "output_passed": {
                        "is_authenticated": True,
                        "error_messages": []
                    }
                },
                {
                    "function_name": "check_roaming_eligibility",
                    "input_passed": {
                        "user_id": "userR3"
                    },
                    "output_passed": {
                        "is_roaming_supported": True,
                        "error_messages": []
                    }
                },
                {
                    "function_name": "activate_roaming",
                    "input_passed": {
                        "user_id": "userR3",
                        "country_code": "MX"
                    },
                    "output_passed": {
                        "roaming_status": "Activated"
                    }
                }
            ],
            "response": (
                "Roaming enabled for Mexico. Enjoy your trip!"
            )
        }
    ]
}
