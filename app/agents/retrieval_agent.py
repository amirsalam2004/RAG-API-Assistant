def retrieval_agent(state, vectordb):

    raw_results = vectordb.search(state.search_query)

    documents = raw_results["documents"][0]
    metadatas = raw_results["metadatas"][0]

    return documents,metadatas