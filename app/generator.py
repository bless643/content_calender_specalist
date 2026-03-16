import os
import json
import re
import uuid
import pandas as pd
from openpyxl.workbook import Workbook
from dotenv import load_dotenv 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

# create LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# create prompt nodes
# 4 workers 

#1st worker 
Sarah_node = ChatPromptTemplate.from_template(
    """
    Your name is Sarah. You work as a content strategist at NeuraRank.
    Your role is to craft a weekly content calendar for NeuraRank.

    NeuraRank company details: {company_details}
    Weekly focus: {weekly_focus}

    Format the output for LinkedIn and Instagram.
    Create 6 rows total:
    - 3 days for LinkedIn
    - 3 days for Instagram
    - alternate platforms by day

    Return a table with 3 columns:
    Day, Topic, Platform
    """
)
# second worker 
john_node = ChatPromptTemplate.from_template(
    """ 
    Your name is John. You work as an associate content strategist at NeuraRank.

    Your role is to take Sarah's table and add a new column called Description.
    The Description column should contain a detailed guide for the content creator on how to properly achieve each deliverable.

    Return the updated table with:
    Day, Topic, Platform, Description

    Sarah's table:
    {Sarah_deliverable}
    """
)
#third worker 
sam_node = ChatPromptTemplate.from_template(
    """
   Your name is Sam. You work as a content editor at NeuraRank.

    Your role is to receive the deliverables from John and improve them for virality, while keeping them relevant to both our target audience and a wider audience.

    Details about NeuraRank:
    {NeuraRank}

    John's deliverables:
    {John_deliverable}
"""
)
#fourth worker 
mercy_node = ChatPromptTemplate.from_template(
    """
   You are a data cleaning assistant at NeuraRank.
    Convert the following messy table into valid JSON.

    Rules:
    - Return only valid JSON
    - Each row should be an object
    - Use consistent column names
    - Do not include explanations

    Messy table:
{table}
"""
)


# create chain 
sarah_chain = Sarah_node | llm
john_chain = john_node | llm
sam_chain = sam_node | llm
mercy_chain = mercy_node | llm

def extract_last_json_block(text: str):
    if not text or not text.strip():
        raise ValueError("Empty output")

    blocks = re.findall(r"```json\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if blocks:
        return json.loads(blocks[-1].strip())

    match = re.search(r"(\[.*\]|\{.*\})", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON found in output")

    return json.loads(match.group(1))

def generate_content_calendar(company_details: str, weekly_focus: str):
    sarah_outcome = sarah_chain.invoke({
        "company_details": company_details,
        "weekly_focus": weekly_focus
    }).content

    john_outcome = john_chain.invoke({
        "Sarah_deliverable": sarah_outcome
    }).content

    sam_outcome = sam_chain.invoke({
        "NeuraRank": company_details,
        "John_deliverable": john_outcome
    }).content

    mercy_outcome = mercy_chain.invoke({
        "table": sam_outcome
    }).content

    data = extract_last_json_block(mercy_outcome)
    df = pd.DataFrame(data)

    os.makedirs("outputs", exist_ok=True)
    filename = f"{uuid.uuid4().hex}.xlsx"
    filepath = os.path.join("outputs", filename)
    df.to_excel(filepath, index=False)

    return {
        "df": df,
        "file_path": filepath,
        "file_name": filename,
        "sarah_outcome": sarah_outcome,
        "john_outcome": john_outcome,
        "sam_outcome": sam_outcome,
        "mercy_outcome": mercy_outcome,
    }