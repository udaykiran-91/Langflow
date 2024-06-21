import time
from uuid import UUID, uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from langflow.custom.directory_reader.directory_reader import DirectoryReader
from langflow.services.deps import get_settings_service


def run_post(client, flow_id, headers, post_data):
    response = client.post(
        f"api/v1/process/{flow_id}",
        headers=headers,
        json=post_data,
    )
    assert response.status_code == 200, response.json()
    return response.json()


# Helper function to poll task status
def poll_task_status(client, headers, href, max_attempts=20, sleep_time=1):
    for _ in range(max_attempts):
        task_status_response = client.get(
            href,
            headers=headers,
        )
        if task_status_response.status_code == 200 and task_status_response.json()["status"] == "SUCCESS":
            return task_status_response.json()
        time.sleep(sleep_time)
    return None  # Return None if task did not complete in time


PROMPT_REQUEST = {
    "name": "string",
    "template": "string",
    "frontend_node": {
        "template": {},
        "description": "string",
        "base_classes": ["string"],
        "name": "",
        "display_name": "",
        "documentation": "",
        "custom_fields": {},
        "output_types": [],
        "field_formatters": {
            "formatters": {"openai_api_key": {}},
            "base_formatters": {
                "kwargs": {},
                "optional": {},
                "list": {},
                "dict": {},
                "union": {},
                "multiline": {},
                "show": {},
                "password": {},
                "default": {},
                "headers": {},
                "dict_code_file": {},
                "model_fields": {
                    "MODEL_DICT": {
                        "OpenAI": [
                            "text-davinci-003",
                            "text-davinci-002",
                            "text-curie-001",
                            "text-babbage-001",
                            "text-ada-001",
                        ],
                        "ChatOpenAI": [
                            "gpt-4-turbo-preview",
                            "gpt-4-0125-preview",
                            "gpt-4-1106-preview",
                            "gpt-4-vision-preview",
                            "gpt-3.5-turbo-0125",
                            "gpt-3.5-turbo-1106",
                        ],
                        "Anthropic": [
                            "claude-v1",
                            "claude-v1-100k",
                            "claude-instant-v1",
                            "claude-instant-v1-100k",
                            "claude-v1.3",
                            "claude-v1.3-100k",
                            "claude-v1.2",
                            "claude-v1.0",
                            "claude-instant-v1.1",
                            "claude-instant-v1.1-100k",
                            "claude-instant-v1.0",
                        ],
                        "ChatAnthropic": [
                            "claude-v1",
                            "claude-v1-100k",
                            "claude-instant-v1",
                            "claude-instant-v1-100k",
                            "claude-v1.3",
                            "claude-v1.3-100k",
                            "claude-v1.2",
                            "claude-v1.0",
                            "claude-instant-v1.1",
                            "claude-instant-v1.1-100k",
                            "claude-instant-v1.0",
                        ],
                    }
                },
            },
        },
    },
}


# def test_process_flow_invalid_api_key(client, flow, monkeypatch):
#     # Mock de process_graph_cached
#     from langflow.api.v1 import endpoints
#     from langflow.services.database.models.api_key import crud

#     settings_service = get_settings_service()
#     settings_service.auth_settings.AUTO_LOGIN = False

#     async def mock_process_graph_cached(*args, **kwargs):
#         return Result(result={}, session_id="session_id_mock")

#     def mock_update_total_uses(*args, **kwargs):
#         return created_api_key

#     monkeypatch.setattr(endpoints, "process_graph_cached", mock_process_graph_cached)
#     monkeypatch.setattr(crud, "update_total_uses", mock_update_total_uses)

#     headers = {"x-api-key": "invalid_api_key"}

#     post_data = {
#         "inputs": {"key": "value"},
#         "tweaks": None,
#         "clear_cache": False,
#         "session_id": None,
#     }

#     response = client.post(f"api/v1/process/{flow.id}", headers=headers, json=post_data)

#     assert response.status_code == 403
#     assert response.json() == {"detail": "Invalid or missing API key"}


# def test_process_flow_invalid_id(client, monkeypatch, created_api_key):
#     async def mock_process_graph_cached(*args, **kwargs):
#         return Result(result={}, session_id="session_id_mock")

#     from langflow.api.v1 import endpoints

#     monkeypatch.setattr(endpoints, "process_graph_cached", mock_process_graph_cached)

#     api_key = created_api_key.api_key
#     headers = {"x-api-key": api_key}

#     post_data = {
#         "inputs": {"key": "value"},
#         "tweaks": None,
#         "clear_cache": False,
#         "session_id": None,
#     }

#     invalid_id = uuid.uuid4()
#     response = client.post(f"api/v1/process/{invalid_id}", headers=headers, json=post_data)

#     assert response.status_code == 404
#     assert f"Flow {invalid_id} not found" in response.json()["detail"]


# def test_process_flow_without_autologin(client, flow, monkeypatch, created_api_key):
#     # Mock de process_graph_cached
#     from langflow.api.v1 import endpoints
#     from langflow.services.database.models.api_key import crud

#     settings_service = get_settings_service()
#     settings_service.auth_settings.AUTO_LOGIN = False

#     async def mock_process_graph_cached(*args, **kwargs):
#         return Result(result={}, session_id="session_id_mock")

#     def mock_process_graph_cached_task(*args, **kwargs):
#         return Result(result={}, session_id="session_id_mock")

#     # The task function is ran like this:
#     # if not self.use_celery:
#     #     return None, await task_func(*args, **kwargs)
#     # if not hasattr(task_func, "apply"):
#     #     raise ValueError(f"Task function {task_func} does not have an apply method")
#     # task = task_func.apply(args=args, kwargs=kwargs)
#     # result = task.get()
#     # return task.id, result
#     # So we need to mock the task function to return a task object
#     # and then mock the task object to return a result
#     # maybe a named tuple would be better here
#     task = namedtuple("task", ["id", "get"])
#     mock_process_graph_cached_task.apply = lambda *args, **kwargs: task(
#         id="task_id_mock", get=lambda: Result(result={}, session_id="session_id_mock")
#     )

#     def mock_update_total_uses(*args, **kwargs):
#         return created_api_key

#     monkeypatch.setattr(endpoints, "process_graph_cached", mock_process_graph_cached)
#     monkeypatch.setattr(crud, "update_total_uses", mock_update_total_uses)
#     monkeypatch.setattr(endpoints, "process_graph_cached_task", mock_process_graph_cached_task)

#     api_key = created_api_key.api_key
#     headers = {"x-api-key": api_key}

#     # Dummy POST data
#     post_data = {
#         "inputs": {"input": "value"},
#         "tweaks": None,
#         "clear_cache": False,
#         "session_id": None,
#     }

#     # Make the request to the FastAPI TestClient

#     response = client.post(f"api/v1/process/{flow.id}", headers=headers, json=post_data)

#     # Check the response
#     assert response.status_code == 200, response.json()
#     assert response.json()["result"] == {}, response.json()
#     assert response.json()["session_id"] == "session_id_mock", response.json()


# def test_process_flow_fails_autologin_off(client, flow, monkeypatch):
#     # Mock de process_graph_cached
#     from langflow.api.v1 import endpoints
#     from langflow.services.database.models.api_key import crud

#     settings_service = get_settings_service()
#     settings_service.auth_settings.AUTO_LOGIN = False

#     async def mock_process_graph_cached(*args, **kwargs):
#         return Result(result={}, session_id="session_id_mock")

#     async def mock_update_total_uses(*args, **kwargs):
#         return created_api_key

#     monkeypatch.setattr(endpoints, "process_graph_cached", mock_process_graph_cached)
#     monkeypatch.setattr(crud, "update_total_uses", mock_update_total_uses)

#     headers = {"x-api-key": "api_key"}

#     # Dummy POST data
#     post_data = {
#         "inputs": {"key": "value"},
#         "tweaks": None,
#         "clear_cache": False,
#         "session_id": None,
#     }

#     # Make the request to the FastAPI TestClient

#     response = client.post(f"api/v1/process/{flow.id}", headers=headers, json=post_data)

#     # Check the response
#     assert response.status_code == 403, response.json()
#     assert response.json() == {"detail": "Invalid or missing API key"}


def test_get_all(client: TestClient, logged_in_headers):
    response = client.get("api/v1/all", headers=logged_in_headers)
    assert response.status_code == 200
    settings = get_settings_service().settings
    dir_reader = DirectoryReader(settings.components_path[0])
    files = dir_reader.get_files()
    # json_response is a dict of dicts
    all_names = [component_name for _, components in response.json().items() for component_name in components]
    json_response = response.json()
    # We need to test the custom nodes
    assert len(all_names) <= len(
        files
    )  # Less or equal because we might have some files that don't have the dependencies installed
    assert "ChatInput" in json_response["inputs"]
    assert "Prompt" in json_response["inputs"]
    assert "ChatOutput" in json_response["outputs"]


def test_post_validate_code(client: TestClient):
    # Test case with a valid import and function
    code1 = """
import math

def square(x):
    return x ** 2
"""
    response1 = client.post("api/v1/validate/code", json={"code": code1})
    assert response1.status_code == 200
    assert response1.json() == {"imports": {"errors": []}, "function": {"errors": []}}

    # Test case with an invalid import and valid function
    code2 = """
import non_existent_module

def square(x):
    return x ** 2
"""
    response2 = client.post("api/v1/validate/code", json={"code": code2})
    assert response2.status_code == 200
    assert response2.json() == {
        "imports": {"errors": ["No module named 'non_existent_module'"]},
        "function": {"errors": []},
    }

    # Test case with a valid import and invalid function syntax
    code3 = """
import math

def square(x)
    return x ** 2
"""
    response3 = client.post("api/v1/validate/code", json={"code": code3})
    assert response3.status_code == 200
    assert response3.json() == {
        "imports": {"errors": []},
        "function": {"errors": ["expected ':' (<unknown>, line 4)"]},
    }

    # Test case with invalid JSON payload
    response4 = client.post("api/v1/validate/code", json={"invalid_key": code1})
    assert response4.status_code == 422

    # Test case with an empty code string
    response5 = client.post("api/v1/validate/code", json={"code": ""})
    assert response5.status_code == 200
    assert response5.json() == {"imports": {"errors": []}, "function": {"errors": []}}

    # Test case with a syntax error in the code
    code6 = """
import math

def square(x)
    return x ** 2
"""
    response6 = client.post("api/v1/validate/code", json={"code": code6})
    assert response6.status_code == 200
    assert response6.json() == {
        "imports": {"errors": []},
        "function": {"errors": ["expected ':' (<unknown>, line 4)"]},
    }


VALID_PROMPT = """
I want you to act as a naming consultant for new companies.

Here are some examples of good company names:

- search engine, Google
- social media, Facebook
- video sharing, YouTube

The name should be short, catchy and easy to remember.

What is a good name for a company that makes {product}?
"""

INVALID_PROMPT = "This is an invalid prompt without any input variable."


def test_valid_prompt(client: TestClient):
    PROMPT_REQUEST["template"] = VALID_PROMPT
    response = client.post("api/v1/validate/prompt", json=PROMPT_REQUEST)
    assert response.status_code == 200
    assert response.json()["input_variables"] == ["product"]


def test_invalid_prompt(client: TestClient):
    PROMPT_REQUEST["template"] = INVALID_PROMPT
    response = client.post(
        "api/v1/validate/prompt",
        json=PROMPT_REQUEST,
    )
    assert response.status_code == 200
    assert response.json()["input_variables"] == []


@pytest.mark.parametrize(
    "prompt,expected_input_variables",
    [
        ("{color} is my favorite color.", ["color"]),
        ("The weather is {weather} today.", ["weather"]),
        ("This prompt has no variables.", []),
        ("{a}, {b}, and {c} are variables.", ["a", "b", "c"]),
    ],
)
def test_various_prompts(client, prompt, expected_input_variables):
    PROMPT_REQUEST["template"] = prompt
    response = client.post("api/v1/validate/prompt", json=PROMPT_REQUEST)
    assert response.status_code == 200
    assert response.json()["input_variables"] == expected_input_variables


def test_get_vertices_flow_not_found(client, logged_in_headers):
    uuid = uuid4()
    response = client.post(f"/api/v1/build/{uuid}/vertices", headers=logged_in_headers)
    assert response.status_code == 500


def test_get_vertices(client, added_flow_with_prompt_and_history, logged_in_headers):
    flow_id = added_flow_with_prompt_and_history["id"]
    response = client.post(f"/api/v1/build/{flow_id}/vertices", headers=logged_in_headers)
    assert response.status_code == 200
    assert "ids" in response.json()
    # The response should contain the list in this order
    # ['ConversationBufferMemory-Lu2Nb', 'PromptTemplate-5Q0W8', 'ChatOpenAI-vy7fV', 'LLMChain-UjBh1']
    # The important part is before the - (ConversationBufferMemory, PromptTemplate, ChatOpenAI, LLMChain)
    ids = [_id.split("-")[0] for _id in response.json()["ids"]]
    assert ids == [
        "ChatOpenAI",
        "PromptTemplate",
        "ConversationBufferMemory",
    ]


def test_build_vertex_invalid_flow_id(client, logged_in_headers):
    uuid = uuid4()
    response = client.post(f"/api/v1/build/{uuid}/vertices/vertex_id", headers=logged_in_headers)
    assert response.status_code == 500


def test_build_vertex_invalid_vertex_id(client, added_flow_with_prompt_and_history, logged_in_headers):
    flow_id = added_flow_with_prompt_and_history["id"]
    response = client.post(f"/api/v1/build/{flow_id}/vertices/invalid_vertex_id", headers=logged_in_headers)
    assert response.status_code == 500


def test_successful_run_no_payload(client, starter_project, created_api_key):
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = starter_project["id"]
    response = client.post(f"/api/v1/run/{flow_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK, response.text
    # Add more assertions here to validate the response content
    json_response = response.json()
    assert "session_id" in json_response
    assert "outputs" in json_response
    outer_outputs = json_response["outputs"]
    assert len(outer_outputs) == 1
    outputs_dict = outer_outputs[0]
    assert len(outputs_dict) == 2
    assert "inputs" in outputs_dict
    assert "outputs" in outputs_dict
    assert outputs_dict.get("inputs") == {"input_value": ""}
    assert isinstance(outputs_dict.get("outputs"), list)
    assert len(outputs_dict.get("outputs")) == 1
    ids = [output.get("component_id") for output in outputs_dict.get("outputs")]
    assert all(["ChatOutput" in _id for _id in ids])
    display_names = [output.get("component_display_name") for output in outputs_dict.get("outputs")]
    assert all([name in display_names for name in ["Chat Output"]])
    inner_results = [output.get("results").get("result") for output in outputs_dict.get("outputs")]

    assert all([result is not None for result in inner_results]), outputs_dict.get("outputs")


def test_successful_run_with_output_type_text(client, starter_project, created_api_key):
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = starter_project["id"]
    payload = {
        "output_type": "text",
    }
    response = client.post(f"/api/v1/run/{flow_id}", headers=headers, json=payload)
    assert response.status_code == status.HTTP_200_OK, response.text
    # Add more assertions here to validate the response content
    json_response = response.json()
    assert "session_id" in json_response
    assert "outputs" in json_response
    outer_outputs = json_response["outputs"]
    assert len(outer_outputs) == 1
    outputs_dict = outer_outputs[0]
    assert len(outputs_dict) == 2
    assert "inputs" in outputs_dict
    assert "outputs" in outputs_dict
    assert outputs_dict.get("inputs") == {"input_value": ""}
    assert isinstance(outputs_dict.get("outputs"), list)
    assert len(outputs_dict.get("outputs")) == 1
    ids = [output.get("component_id") for output in outputs_dict.get("outputs")]
    assert all(["ChatOutput" in _id for _id in ids]), ids
    display_names = [output.get("component_display_name") for output in outputs_dict.get("outputs")]
    assert all([name in display_names for name in ["Chat Output"]]), display_names
    inner_results = [output.get("results").get("result") for output in outputs_dict.get("outputs")]
    expected_result = ""
    assert all([expected_result in result for result in inner_results]), inner_results


def test_successful_run_with_output_type_any(client, starter_project, created_api_key):
    # This one should have both the ChatOutput and TextOutput components
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = starter_project["id"]
    payload = {
        "output_type": "any",
    }
    response = client.post(f"/api/v1/run/{flow_id}", headers=headers, json=payload)
    assert response.status_code == status.HTTP_200_OK, response.text
    # Add more assertions here to validate the response content
    json_response = response.json()
    assert "session_id" in json_response
    assert "outputs" in json_response
    outer_outputs = json_response["outputs"]
    assert len(outer_outputs) == 1
    outputs_dict = outer_outputs[0]
    assert len(outputs_dict) == 2
    assert "inputs" in outputs_dict
    assert "outputs" in outputs_dict
    assert outputs_dict.get("inputs") == {"input_value": ""}
    assert isinstance(outputs_dict.get("outputs"), list)
    assert len(outputs_dict.get("outputs")) == 1
    ids = [output.get("component_id") for output in outputs_dict.get("outputs")]
    assert all(["ChatOutput" in _id or "TextOutput" in _id for _id in ids]), ids
    display_names = [output.get("component_display_name") for output in outputs_dict.get("outputs")]
    assert all([name in display_names for name in ["Chat Output"]]), display_names
    inner_results = [output.get("results").get("result") for output in outputs_dict.get("outputs")]
    expected_result = ""
    assert all([expected_result in result for result in inner_results]), inner_results


def test_successful_run_with_output_type_debug(client, starter_project, created_api_key):
    # This one should return outputs for all components
    # Let's just check the amount of outputs(there should be 7)
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = starter_project["id"]
    payload = {
        "output_type": "debug",
    }
    response = client.post(f"/api/v1/run/{flow_id}", headers=headers, json=payload)
    assert response.status_code == status.HTTP_200_OK, response.text
    # Add more assertions here to validate the response content
    json_response = response.json()
    assert "session_id" in json_response
    assert "outputs" in json_response
    outer_outputs = json_response["outputs"]
    assert len(outer_outputs) == 1
    outputs_dict = outer_outputs[0]
    assert len(outputs_dict) == 2
    assert "inputs" in outputs_dict
    assert "outputs" in outputs_dict
    assert outputs_dict.get("inputs") == {"input_value": ""}
    assert isinstance(outputs_dict.get("outputs"), list)
    assert len(outputs_dict.get("outputs")) == 4


# To test input_type wel'l just set it with output_type debug and check if the value is correct
def test_successful_run_with_input_type_text(client, starter_project, created_api_key):
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = starter_project["id"]
    payload = {
        "input_type": "text",
        "output_type": "debug",
        "input_value": "value1",
    }
    response = client.post(f"/api/v1/run/{flow_id}", headers=headers, json=payload)
    assert response.status_code == status.HTTP_200_OK, response.text
    # Add more assertions here to validate the response content
    json_response = response.json()
    assert "session_id" in json_response
    assert "outputs" in json_response
    outer_outputs = json_response["outputs"]
    assert len(outer_outputs) == 1
    outputs_dict = outer_outputs[0]
    assert len(outputs_dict) == 2
    assert "inputs" in outputs_dict
    assert "outputs" in outputs_dict
    assert outputs_dict.get("inputs") == {"input_value": "value1"}
    assert isinstance(outputs_dict.get("outputs"), list)
    assert len(outputs_dict.get("outputs")) == 4
    # Now we get all components that contain TextInput in the component_id
    text_input_outputs = [output for output in outputs_dict.get("outputs") if "TextInput" in output.get("component_id")]
    assert len(text_input_outputs) == 0
    # Now we check if the input_value is correct
    assert all([output.get("results").get("result") == "value1" for output in text_input_outputs]), text_input_outputs


# Now do the same for "chat" input type
def test_successful_run_with_input_type_chat(client, starter_project, created_api_key):
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = starter_project["id"]
    payload = {
        "input_type": "chat",
        "output_type": "debug",
        "input_value": "value1",
    }
    response = client.post(f"/api/v1/run/{flow_id}", headers=headers, json=payload)
    assert response.status_code == status.HTTP_200_OK, response.text
    # Add more assertions here to validate the response content
    json_response = response.json()
    assert "session_id" in json_response
    assert "outputs" in json_response
    outer_outputs = json_response["outputs"]
    assert len(outer_outputs) == 1
    outputs_dict = outer_outputs[0]
    assert len(outputs_dict) == 2
    assert "inputs" in outputs_dict
    assert "outputs" in outputs_dict
    assert outputs_dict.get("inputs") == {"input_value": "value1"}
    assert isinstance(outputs_dict.get("outputs"), list)
    assert len(outputs_dict.get("outputs")) == 4
    # Now we get all components that contain TextInput in the component_id
    chat_input_outputs = [output for output in outputs_dict.get("outputs") if "ChatInput" in output.get("component_id")]
    assert len(chat_input_outputs) == 1
    # Now we check if the input_value is correct
    assert all([output.get("results").get("result") == "value1" for output in chat_input_outputs]), chat_input_outputs


def test_successful_run_with_input_type_any(client, starter_project, created_api_key):
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = starter_project["id"]
    payload = {
        "input_type": "any",
        "output_type": "debug",
        "input_value": "value1",
    }
    response = client.post(f"/api/v1/run/{flow_id}", headers=headers, json=payload)
    assert response.status_code == status.HTTP_200_OK, response.text
    # Add more assertions here to validate the response content
    json_response = response.json()
    assert "session_id" in json_response
    assert "outputs" in json_response
    outer_outputs = json_response["outputs"]
    assert len(outer_outputs) == 1
    outputs_dict = outer_outputs[0]
    assert len(outputs_dict) == 2
    assert "inputs" in outputs_dict
    assert "outputs" in outputs_dict
    assert outputs_dict.get("inputs") == {"input_value": "value1"}
    assert isinstance(outputs_dict.get("outputs"), list)
    assert len(outputs_dict.get("outputs")) == 4
    # Now we get all components that contain TextInput or ChatInput in the component_id
    any_input_outputs = [
        output
        for output in outputs_dict.get("outputs")
        if "TextInput" in output.get("component_id") or "ChatInput" in output.get("component_id")
    ]
    assert len(any_input_outputs) == 1
    # Now we check if the input_value is correct
    assert all([output.get("results").get("result") == "value1" for output in any_input_outputs]), any_input_outputs


@pytest.mark.api_key_required
def test_run_with_inputs_and_outputs(client, starter_project, created_api_key):
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = starter_project["id"]
    payload = {
        "input_value": "value1",
        "input_type": "text",
        "output_type": "text",
        "tweaks": {"parameter_name": "value"},
        "stream": False,
    }
    response = client.post(f"/api/v1/run/{flow_id}", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK, response.text
    # Validate the response structure and content


def test_invalid_flow_id(client, created_api_key):
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = "invalid-flow-id"
    response = client.post(f"/api/v1/run/{flow_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = UUID(int=0)
    response = client.post(f"/api/v1/run/{flow_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    # Check if the error detail is as expected


@pytest.mark.api_key_required
def test_run_flow_with_caching_success(client: TestClient, starter_project, created_api_key):
    flow_id = starter_project["id"]
    headers = {"x-api-key": created_api_key.api_key}
    payload = {
        "input_value": "value1",
        "input_type": "text",
        "output_type": "text",
        "tweaks": {"parameter_name": "value"},
        "stream": False,
    }
    response = client.post(f"/api/v1/run/{flow_id}", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "outputs" in data
    assert "session_id" in data


@pytest.mark.api_key_required
def test_run_flow_with_caching_invalid_flow_id(client: TestClient, created_api_key):
    invalid_flow_id = uuid4()
    headers = {"x-api-key": created_api_key.api_key}
    payload = {"input_value": "", "input_type": "text", "output_type": "text", "tweaks": {}, "stream": False}
    response = client.post(f"/api/v1/run/{invalid_flow_id}", json=payload, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert f"Flow identifier {invalid_flow_id} not found" in data["detail"]


@pytest.mark.api_key_required
def test_run_flow_with_caching_invalid_input_format(client: TestClient, starter_project, created_api_key):
    flow_id = starter_project["id"]
    headers = {"x-api-key": created_api_key.api_key}
    payload = {"input_value": {"key": "value"}, "input_type": "text", "output_type": "text", "tweaks": {}}
    response = client.post(f"/api/v1/run/{flow_id}", json=payload, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.api_key_required
def test_run_flow_with_session_id(client, starter_project, created_api_key):
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = starter_project["id"]
    payload = {
        "input_value": "value1",
        "input_type": "text",
        "output_type": "text",
        "session_id": "test-session-id",
    }
    response = client.post(f"/api/v1/run/{flow_id}", json=payload, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert {"detail": "Session test-session-id not found"} == data


def test_run_flow_with_invalid_session_id(client, starter_project, created_api_key):
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = starter_project["id"]
    payload = {
        "input_value": "value1",
        "input_type": "text",
        "output_type": "text",
        "session_id": "invalid-session-id",
    }
    response = client.post(f"/api/v1/run/{flow_id}", json=payload, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert f"Session {payload['session_id']} not found" in data["detail"]


@pytest.mark.api_key_required
def test_run_flow_with_invalid_tweaks(client, starter_project, created_api_key):
    headers = {"x-api-key": created_api_key.api_key}
    flow_id = starter_project["id"]
    payload = {
        "input_value": "value1",
        "input_type": "text",
        "output_type": "text",
        "tweaks": {"invalid_tweak": "value"},
    }
    response = client.post(f"/api/v1/run/{flow_id}", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
