from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ollama import Client
import time


class OllamaTranslator:
    def __init__(
        self,
        model="llama3.2",
        temperature=0.0,
        max_tokens=512,
        seed=42,
        context=2048,
        num_threads=4,
        retries=3,
        delay=1.0,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed
        self.context = context
        self.num_threads = num_threads
        self.retries = retries
        self.delay = delay

    def translate_parallel(self, tasks):
        """
        tasks: list[str] — список фраз для перевода
        Возвращает: list[str] — переведённые строки
        """
        results = []
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            future_to_task = {
                executor.submit(self._translate_with_retry, text): text
                for text in tasks
            }
            for future in tqdm(
                as_completed(future_to_task),
                total=len(future_to_task),
                desc="Translating",
                mininterval=0.2,
            ):
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append(f"[ОШИБКА] {str(e)}")
        return results

    def _translate_with_retry(self, text):
        for attempt in range(self.retries):
            try:
                return self._translate(text)
            except Exception as e:
                time.sleep(self.delay)
        return f"[ОШИБКА ПЕРЕВОДА]: {text}"

    def _translate(self, text):
        client = Client(host="http://localhost:11434")
        prompt = (
            f"Переведи следующий текст с английского на русский язык.\n"
            f"Верни только перевод без пояснений, без кавычек, без альтернатив.\n\n{text}"
        )

        response = client.generate(
            model=self.model,
            prompt=prompt,
            options={
                "temperature": self.temperature,
                "seed": self.seed,
                "num_predict": self.max_tokens,
                "num_ctx": self.context,
            },
        )
        return response["response"].strip().split("\n")[0]


if __name__ == "__main__":
    import pandas as pd

    df = pd.read_csv("data/data.csv")
    temp = df.head(100).copy()
    questions = temp["question"].tolist()

    translator = OllamaTranslator(model="llama3.2", num_threads=4)
    translations = translator.translate_parallel(questions)

    temp["question_ru"] = translations
    temp.to_csv("data/translated_dataset.csv", index=False)
