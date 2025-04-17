import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from agents import Agent, Runner, WebSearchTool, function_tool, trace, gen_trace_id

# Simple models with minimal schema
class ResearchReport(BaseModel):
    main_findings: str = Field(description="A concise summary of the main findings (3-4 sentences)")
    detailed_analysis: str = Field(description="A detailed analysis of the research topic (500-1000 words)")
    sources: list[str] = Field(description="List of sources used in the research")
    follow_up_questions: list[str] = Field(description="Suggested follow-up questions for deeper exploration")

# Simple tools with minimal parameters
@function_tool
async def read_webpage(url: str) -> str:
    """
    Directly read and extract content from a webpage URL.
    
    Args:
        url: The webpage URL to read
        
    Returns:
        The extracted text content from the webpage
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.extract()
                    
                    # Extract text
                    text = soup.get_text(separator='\n')
                    
                    # Clean up text (remove extra whitespace)
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    # Return a reasonable amount of text
                    return text[:8000] + "..." if len(text) > 8000 else text
                else:
                    return f"Failed to retrieve the webpage. Status code: {response.status}"
    except Exception as e:
        return f"Error reading webpage: {str(e)}"

# Research agents
search_agent = Agent(
    name="Search Agent",
    instructions="""You are an expert web search agent specializing in finding relevant information for research.
    
    Your tasks:
    1. Execute effective web searches based on the research query
    2. Analyze search results to identify the most relevant information
    3. Read web pages to extract detailed content when necessary
    
    Be thorough in your search approach. Try different search queries to get diverse results.
    Look for academic and authoritative sources when possible.
    """,
    tools=[
        WebSearchTool(user_location={"type": "approximate", "city": "New York"}),
        read_webpage
    ]
)

analysis_agent = Agent(
    name="Analysis Agent",
    instructions="""You are an expert research analyst specializing in synthesizing information into coherent findings.
    
    Your tasks:
    1. Analyze all the collected information from the search phase
    2. Identify key themes, patterns, and insights
    3. Develop a comprehensive understanding of the research topic
    4. Formulate main findings and detailed analysis
    5. List important sources and suggest follow-up questions
    
    Your analysis should be:
    - Comprehensive and balanced, presenting multiple viewpoints
    - Structured logically with clear sections
    - Based on factual information from reliable sources
    - Academically rigorous while remaining accessible
    """,
    output_type=ResearchReport
)

async def perform_research(query: str) -> ResearchReport:
    """
    Execute a deep research process on the given query.
    
    Args:
        query: The research question or topic
    
    Returns:
        A structured research report
    """
    # Generate a trace ID for monitoring
    trace_id = gen_trace_id()
    
    # Create a trace to track the entire research process
    with trace("Deep Research Process", trace_id=trace_id):
        print(f"Starting research on: {query}")
        print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
        
        # Phase 1: Information gathering using the search agent
        print("Phase 1: Gathering information...")
        search_result = await Runner.run(
            search_agent,
            f"Research query: {query}\n\nConduct thorough web searches to gather information about this topic. Use different search queries to get diverse results. Read key web pages to extract detailed information."
        )
        
        # Phase 2: Analysis and synthesis
        print("Phase 2: Analyzing and synthesizing research...")
        analysis_input = (
            f"Research Query: {query}\n\n"
            f"Previous research findings:\n{search_result.final_output}\n\n"
            f"Based on the above information, create a comprehensive research report with:\n"
            f"1. Main findings (3-4 sentences)\n"
            f"2. Detailed analysis (500-1000 words)\n"
            f"3. List of key sources\n"
            f"4. Follow-up questions for deeper exploration"
        )
        
        analysis_result = await Runner.run(
            analysis_agent,
            analysis_input
        )
        
        # Extract the final research report
        final_report = analysis_result.final_output_as(ResearchReport)
        print("Research complete!")
        
        return final_report

async def main():
    # Get the research query from the user
    query = input("What would you like to research? ")
    
    # Perform the research
    report = await perform_research(query)
    
    # Display the results
    print("\n----- RESEARCH REPORT -----\n")
    print("MAIN FINDINGS:")
    print(report.main_findings)
    print("\nDETAILED ANALYSIS:")
    print(report.detailed_analysis)
    print("\nSOURCES:")
    for i, source in enumerate(report.sources, 1):
        print(f"{i}. {source}")
    print("\nFOLLOW-UP QUESTIONS:")
    for i, question in enumerate(report.follow_up_questions, 1):
        print(f"{i}. {question}")

if __name__ == "__main__":
    asyncio.run(main())
