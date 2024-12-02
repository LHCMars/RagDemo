from flask import Flask
from database import get_chroma_db
from flask import request, jsonify

app = Flask(__name__)


@app.route("/chat", methods=["POST"])
def rag():
    data = request.json
    print(data)
    user = data.get("user")
    scene = data.get("scene")
    query = data.get("query")

    if not user or not scene or not query:
        return (
            jsonify(
                {"error": "Please provide all required fields (user, scene, query)."}
            ),
            400,
        )

    # Retrieve the filtered retriever
    chroma_db = get_chroma_db()
    query_conditions = {
        "$and": [
            {"user": user},  # 替换为你要查询的 user 值
            {"scene": scene},  # 替换为你要查询的 scene 值
        ]
    }

    prompt_results = chroma_db.get(where=query_conditions)  # Get texts with metadata

    # Retrieve the prompt information
    if prompt_results:
        prompt_metadata = prompt_results.get("metadatas")[0]
        prompt_text = prompt_metadata.get("prompt")
    else:
        return (
            jsonify(
                {"error": "No matching prompt found for specified user and scene."}
            ),
            404,
        )

    retriever_with_filter = chroma_db.as_retriever(
        search_kwargs={
            "k": 5,
            "filter": {"$and": [{"user": {"$eq": user}}, {"scene": {"$eq": scene}}]},
        },
    )

    results = retriever_with_filter.invoke(query.replace("あなた", "源頼光"))

    context = ""
    for i in results:
        context += i.page_content

    response = get_system_message().format(prompt=prompt_text, context=context)
    print(response)

    return jsonify({"response": response}), 200


def get_system_message():

    template = (
        "あなたの設定は次の通りです：{prompt}。\n"
        "これから、あなたが知っている内容に関する質問をします。\n"
        "回答は簡潔かつ明確に、1～2文以内で答えてください。\n"
        "必要最低限の情報のみを伝え、追加の説明や展開は行わないでください。\n"
        "質問の文脈は以下に記載されています：{context}。"
    )

    return template


if __name__ == "__main__":
    app.run(debug=True, port=5001)
