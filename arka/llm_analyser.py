from utils import openai_key
import openai
import itertools
from duckduckgo_search import DDGS


class LLMAnalyser:
    """for a given ticker, this will use ai to get the percentage of news articles which are bearish, bullish or mixed"""
    def __init__(self, term: str, n: int = 10):
        self.term = term
        self.n = n
        self.base_string = self.get_news()
        openai.api_key = openai_key()
        self.SYSTEM_PROMPT = """You are a world class financial analyst. 
                  Your role is to take news articles and provide an estimate on the whether they are bullish or bearish for the ticker in question.
                  Your reply should be 'bullish', 'bearish' or 'mixed'. 
                  Never reply with more than one word"""

    def get_news(self) -> str:
        base_string = ""
        with DDGS() as ddgs:
            keywords = self.term
            ddgs_news_gen = ddgs.news(
                keywords,
                region="wt-wt",
                safesearch="Off",
                timelimit="d",
            )

            for i, result in enumerate(list(itertools.islice(ddgs_news_gen, self.n))):
                base_string += f"""\n   {i} TITLE: {result["title"]},BODY: {result["body"]},SOURCE: {result["source"]}
                                """
        return base_string

    def get_ai_summary(self):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": self.base_string},
            ],
        )

        output = response["choices"][0]["message"]["content"]
        lines = output.split("\n")
        total_lines = len(lines)

        bearish_percentage = (
            sum([1 for line in lines if "bearish" in line.lower()]) / total_lines
        ) * 100
        bullish_percentage = (
            sum([1 for line in lines if "bullish" in line.lower()]) / total_lines
        ) * 100
        mixed_percentage = (
            sum([1 for line in lines if "mixed" in line.lower()]) / total_lines
        ) * 100

        return {
            "Bearish": bearish_percentage,
            "Bullish": bullish_percentage,
            "Mixed": mixed_percentage,
        }
