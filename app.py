from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
from crewai import Crew, Agent, Task
import streamlit as st
import json
from pathlib import Path
from langchain_openai import ChatOpenAI
import uuid
from dotenv import load_dotenv
import re

load_dotenv()

# Initialize the LLM
#llm = ChatOpenAI(
    #model="huihui_ai/qwen2.5-1m-abliterated:14b",
    #model="qwen2.5-coder:14b",
    #openai_api_base="http://localhost:11434/v1",  
    #openai_api_key="NA"  
#)
# Initialize the LLM
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct-1M")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct-1M")
llm = pipeline("text-generation", model=model, tokenizer=tokenizer)

def load_input_file(file):
    """Load and parse input JSON file"""
    try:
        content = json.load(file)
        if not isinstance(content, dict):
            st.error("Invalid JSON format: Must be a JSON object")
            return None
        # Validate essential Tableau Prep flow structure
        if not any(key in content for key in ['nodes', 'connections', 'flowVersion']):
            st.warning("Warning: Input may not be a valid Tableau Prep flow file")
        st.success("Successfully loaded input file")
        return content
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON format: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def analyze_flow_with_llm(flow_data):
    """Use LLM to analyze the Tableau Prep flow structure and transformations"""
    analysis_agent = Agent(
        role="Tableau Prep Flow Analyzer",
        goal="Analyze Tableau Prep flow structure and recommend specific Tableau Prep transformations",
        backstory="""You are a Tableau Prep expert who specializes in:
        1. Tableau Prep Builder transformations and operations
        2. Data cleaning and preparation best practices
        3. Flow optimization techniques
        4. Performance tuning for Tableau Prep""",
        llm=llm,
        verbose=True
    )

    analysis_task = Task(
        description=f"""
        Analyze this Tableau Prep Flow and provide Tableau-specific recommendations:

        {json.dumps(flow_data, indent=2)}

        1. ANALYZE CURRENT TABLEAU PREP OPERATIONS:
           - Input Steps: Identify data source configurations
           - Clean Steps: List all cleaning operations (Split, Merge, Remove)
           - Transform Steps: Document pivot/unpivot, aggregations, calculations
           - Output Steps: Review output configurations

        2. IDENTIFY TABLEAU PREP SPECIFIC OPTIMIZATIONS:
           - Group Similar Cleaning Steps: Combine related operations
           - Optimize Step Order: Arrange for better performance
           - Improve Calculations: Use Tableau Prep functions effectively
           - Enhance Data Types: Proper type assignments
           - Filter Placement: Optimize filter positions
           - Join/Union Strategy: Improve data combining methods

        3. PROVIDE TABLEAU PREP TRANSFORMATION INSTRUCTIONS:
           - Specific Tableau Prep operations to add/modify
           - Step-by-step transformation sequence
           - Calculation improvements using Tableau Prep functions
           - Cleaning step consolidation recommendations
           - Filter and grouping optimizations

        Format your response as:
        1. CURRENT TABLEAU PREP STRUCTURE: (existing operations)
        2. OPTIMIZATION RECOMMENDATIONS: (Tableau-specific improvements)
        3. TRANSFORMATION STEPS: (detailed Tableau Prep operations)
        """,
        expected_output="Detailed Tableau Prep analysis and transformation recommendations",
        agent=analysis_agent
    )

    return analysis_task

def display_flow_analysis(analysis):
    """Display detailed flow analysis in Streamlit"""
    st.subheader("Detailed Flow Analysis")
    
    with st.expander("Data Sources"):
        for source in analysis['data_sources']:
            st.write(f"Source ID: {source['id']}")
            st.write(f"Type: {source['type']}")
            st.write(f"Properties: {json.dumps(source['properties'], indent=2)}")
            st.write("---")
    
    with st.expander("Transformations"):
        for transform in analysis['transformations']:
            st.write(f"Transform ID: {transform['id']}")
            st.write(f"Type: {transform['type']}")
            st.write(f"Properties: {json.dumps(transform['properties'], indent=2)}")
            st.write("---")
    
    with st.expander("Filters"):
        for filter in analysis['filters']:
            st.write(f"Filter ID: {filter['id']}")
            st.write(f"Properties: {json.dumps(filter['properties'], indent=2)}")
            st.write("---")
    
    with st.expander("Joins"):
        for join in analysis['joins']:
            st.write(f"Join ID: {join['id']}")
            st.write(f"Properties: {json.dumps(join['properties'], indent=2)}")
            st.write("---")
    
    with st.expander("Aggregations"):
        for agg in analysis['aggregations']:
            st.write(f"Aggregation ID: {agg['id']}")
            st.write(f"Properties: {json.dumps(agg['properties'], indent=2)}")
            st.write("---")

def create_variation_agent(template_flow, flow_analysis_text):
    """Create an agent responsible for generating a complete variation"""
    return Agent(
        role="Tableau Prep Flow Expert",
        goal="Analyze and create an optimized variation of the Tableau Prep Flow while preserving its exact structure and functionality",
        backstory=f"""You are a Tableau Prep Flow expert who has analyzed this flow:
        
        Flow Analysis:
        {flow_analysis_text}
        
        
        Your expertise includes:
        1. Deep understanding of Tableau Prep's JSON structure
        2. Complex data transformation workflows
        3. Advanced optimization techniques
        4. Data lineage preservation""",
        llm=llm,
        verbose=True
    )

def create_critic_agent():
    """Create an agent responsible for reviewing and refining the variation"""
    return Agent(
        role="Tableau Prep Flow Reviewer",
        goal="Critically review and validate the generated variation matches input structure.",
        backstory="""A data engineering specialist who:
        1. Validates all input nodes are preserved in output
        2. Ensures all connections maintain data lineage
        3. Verifies optimization improvements
        4. Guarantees metadata consistency""",
        llm=llm,
        verbose=True
    )

def validate_output(generated_json, template_flow):
    """Validate the output structure"""
    try:
        # Convert string to JSON if needed
        if isinstance(generated_json, str):
            # Clean up the response text
            clean_json = generated_json
            
            # Remove any markdown or text before the JSON
            if '```json' in clean_json:
                clean_json = clean_json.split('```json')[1].split('```')[0]
            elif '```' in clean_json:
                clean_json = clean_json.split('```')[1].split('```')[0]
                
            # Find the actual JSON content
            json_start = clean_json.find('{')
            json_end = clean_json.rfind('}') + 1
            if json_start >= 0 and json_end > 0:
                clean_json = clean_json[json_start:json_end]
            
            # Remove any trailing commas before closing braces/brackets
            clean_json = re.sub(r',(\s*[}\]])', r'\1', clean_json)
            
            # Parse the cleaned JSON
            try:
                generated_json = json.loads(clean_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {str(e)}")
        
        # Basic structure validation
        required_keys = {'parameters', 'selection', 'minorVersion', 'initialNodes', 
                        'nodes', 'majorVersion', 'connections', 'connectionIds'}
        
        missing_keys = required_keys - set(generated_json.keys())
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")
        
        return generated_json
    except Exception as e:
        raise ValueError(f"Validation error: {str(e)}")

def create_variation_task(flow_data, analysis_result, variation_agent):
    """Create a task for generating the Tableau Prep variation"""
    return Task(
        description=f"""
        Based on the Tableau Prep analysis and recommendations:
        {analysis_result}

        Generate a COMPLETE Tableau Prep flow variation that MUST include ALL required elements.
        Use this template structure:
        {{
            "parameters": {{}},
            "selection": {{}},
            "minorVersion": {flow_data.get('minorVersion', 0)},
            "majorVersion": {flow_data.get('majorVersion', 0)},
            "initialNodes": [],
            "nodes": {{
                // Include all node definitions here with proper Tableau Prep types:
                // - Input nodes (.v1.LoadCsv, .v1.LoadExcel)
                // - Transform nodes (.v1.ChangeColumnType, .v1.Filter)
                // - Output nodes (.v1.WriteToHyper, .v1.WriteToCsv)
            }},
            "connections": {{}},
            "connectionIds": []
        }}

        Original flow for reference:
        {json.dumps(flow_data, indent=2)}

        CRITICAL REQUIREMENTS:
        1. MUST include ALL these elements:
           - parameters (even if empty {{}})
           - selection (even if empty {{}})
           - minorVersion (use original or 0)
           - majorVersion (use original or 0)
           - initialNodes (array of node IDs)
           - nodes (object with all node definitions)
           - connections (object with connection definitions)
           - connectionIds (array of connection IDs)

        2. Each node MUST have:
           - nodeType (proper Tableau Prep type)
           - name
           - id (unique identifier)
           - baseType
           - nextNodes
           - properties specific to its type

        Return COMPLETE, VALID JSON with ALL required elements.
        """,
        expected_output="Complete Tableau Prep flow JSON with all required elements",
        agent=variation_agent
    )

def main():
    st.title("Tableau Prep Flow Complete Variation Generator")

    uploaded_file = st.file_uploader("Upload Tableau Prep Flow JSON", type=['json'])

    if uploaded_file:
        flow_data = load_input_file(uploaded_file)
        if flow_data:
            with st.spinner("Analyzing flow structure..."):
                try:
                    analysis_task = analyze_flow_with_llm(flow_data)
                    analysis_crew = Crew(
                        agents=[Agent(
                            role="Tableau Prep Flow Analyzer",
                            goal="Analyze flow structure",
                            backstory="Expert in Tableau Prep flows",
                            llm=llm,
                            verbose=True
                        )],
                        tasks=[analysis_task]
                    )
                    
                    analysis_result = analysis_crew.kickoff()
                    st.header("Flow Analysis")
                    st.markdown(analysis_result)

                    # Create variation based on analysis
                    variation_agent = create_variation_agent(flow_data, analysis_result)
                    critic_agent = create_critic_agent()
                    
                    if st.button("Generate and Review Variation"):
                        with st.spinner("Generating Complete Variation..."):
                            try:
                                variation_task = create_variation_task(flow_data, analysis_result, variation_agent)
                                
                                crew = Crew(
                                    agents=[variation_agent, critic_agent],
                                    tasks=[variation_task]
                                )
                                
                                result = crew.kickoff()
                                final_result = validate_output(result, flow_data)
                                
                                # Save and display results
                                output_dir = Path("variations")
                                output_dir.mkdir(exist_ok=True)
                                output_file = output_dir / f"optimized_flow_{uuid.uuid4()}.json"

                                with open(output_file, 'w') as f:
                                    json.dump(final_result, f, indent=2)

                                st.success(f"Variation generated and saved to {output_file}")
                                
                                # Display comparison
                                with st.expander("Compare Flows"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.subheader("Original Flow")
                                        st.json(flow_data)
                                    with col2:
                                        st.subheader("Optimized Flow")
                                        st.json(final_result)

                            except Exception as e:
                                st.error(f"Error in variation generation: {str(e)}")
                                st.error("Please ensure the input JSON is a valid Tableau Prep flow file")

                except Exception as e:
                    st.error(f"Error in flow analysis: {str(e)}")

if __name__ == "__main__":
    main()
