from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def create_vector_store(video_id):

    vector_path = f"vectorstores/{video_id}"

    if os.path.exists(vector_path):
        print("Already indexed")
        return

    yt_api = YouTubeTranscriptApi()

    try:
        transcript_list = yt_api.fetch(
            video_id=video_id,
            languages=['en']
        )
    except:
        transcript_list = yt_api.fetch(video_id=video_id)

    transcript = " ".join(
        chunk.text
        for chunk in transcript_list
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.create_documents([transcript])

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    os.makedirs("vectorstores", exist_ok=True)

    vector_store.save_local(
        f"vectorstores/{video_id}"
    )

def ask_question(video_id, question):

    vector_store = FAISS.load_local(
        f"vectorstores/{video_id}",
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k":4}
    )

    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.
        Answer ONLY from the transcript.
        If the answer is not present, say you don't know.

        Context:
        {context}

        Question:
        {question}
        """,
        input_variables=["context", "question"]
    )

    def format_docs(docs):
        return "\n\n".join(
            doc.page_content
            for doc in docs
        )

    parallel_chain = RunnableParallel({
        'context': retriever | RunnableLambda(format_docs), # big context string
        'question':RunnablePassthrough()
    })

    parser = StrOutputParser()

    chain = parallel_chain | prompt | llm | parser

    return chain.invoke(question)



if __name__ == "__main__":

    video_id = "o126p1QN_RI"

    create_vector_store(video_id)

    answer = ask_question(
        video_id,
        "What is RAG?"
    )

    print(answer)