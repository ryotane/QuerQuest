from pypdf import PdfReader
from ai_agent.memory.vector_memory import VectorMemory

def load_pdf(path):
    vm = VectorMemory()
    reader = PdfReader(path)

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            vm.add(text, {"source": path, "page": i})

    vm.save()