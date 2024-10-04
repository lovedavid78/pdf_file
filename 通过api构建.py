from gradio_client import Client

client = Client("http://127.0.0.1:7863/")
result = client.predict(
		message={"text":"","files":[]},
		api_name="/chat"
)
print(result)