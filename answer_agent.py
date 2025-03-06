from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import networkx as nx
from langchain_openai import ChatOpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnswerDraftingAgent:
    def __init__(self):
        # Initialize LangChain components
        self.llm = ChatOpenAI()
        
        # Define the synthesis prompt template
        self.synthesis_prompt = PromptTemplate(
            input_variables=["research_data"],
            template="""
            Based on the following research data, provide a comprehensive and well-structured answer:
            
            Research Data:
            {research_data}
            
            Please analyze the information and provide:
            1. A concise summary
            2. Key findings and insights
            3. Supporting evidence and sources
            4. Any potential limitations or gaps in the research
            
            Answer:
            """
        )
        
        # Create the synthesis chain using the new pattern
        self.synthesis_chain = self.synthesis_prompt | self.llm | StrOutputParser()
        
        # Initialize knowledge graph
        self.knowledge_graph = nx.DiGraph()

    def _build_knowledge_graph(self, research_results: List[Dict[str, Any]]):
        """
        Build a knowledge graph from research results
        """
        # Clear previous graph
        self.knowledge_graph.clear()
        
        for result in research_results:
            # Add nodes for each piece of information
            self.knowledge_graph.add_node(
                result["query"],
                type="query"
            )
            
            for item in result.get("results", []):
                # Add nodes for each search result
                self.knowledge_graph.add_node(
                    item["url"],
                    type="source",
                    title=item["title"],
                    score=item["score"]
                )
                
                # Add edges between query and results
                self.knowledge_graph.add_edge(
                    result["query"],
                    item["url"],
                    relation="found_in"
                )

    async def synthesize_research(self, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize research results into a coherent answer
        """
        try:
            # Build knowledge graph from research results
            self._build_knowledge_graph(research_results)
            
            # Prepare research data for synthesis
            research_data = "\n\n".join([
                f"Query: {result['query']}\n" +
                "\n".join([
                    f"- {r['title']}: {r['content'][:500]}..."
                    for r in result.get("results", [])
                ])
                for result in research_results
            ])
            
            # Generate synthesis using LangChain
            synthesis = await self.synthesis_chain.ainvoke({"research_data": research_data})
            
            # Convert NetworkX graph to dictionary format
            graph_data = {
                "nodes": [{"id": n, **self.knowledge_graph.nodes[n]} for n in self.knowledge_graph.nodes()],
                "edges": [{"source": u, "target": v, **d} for u, v, d in self.knowledge_graph.edges(data=True)]
            }
            
            return {
                "synthesis": synthesis,
                "knowledge_graph": graph_data,
                "source_count": len([r for result in research_results for r in result.get("results", [])])
            }
            
        except Exception as e:
            logger.error(f"Error during synthesis: {str(e)}")
            return {
                "error": str(e),
                "synthesis": "",
                "knowledge_graph": {},
                "source_count": 0
            } 