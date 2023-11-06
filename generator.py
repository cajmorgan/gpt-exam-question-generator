from PIL import Image
import pytesseract
import fitz
import os
import re


print("Loading PDFs... ")
# Remove non-pdf files from directory
pdf_files = os.listdir("./pdfs")
for i in range(len(pdf_files) - 1, -1, -1):
    if not re.search(".pdf", pdf_files[i]):
        del pdf_files[i]

pdf_files.sort()
pdf_files

gpt_limit = 14500
prompt_parts = []

for file in pdf_files:
    print(f"Working on {file}...")
    doc = fitz.open("./pdfs/" + file)
    pages = doc.page_count

    current_part = ""

    for page_num in range(pages):
        page = doc.load_page(page_num)
        image = page.get_pixmap()
        image.save(f"page_{page_num + 1}.png", "png")
        image_path = f"page_{page_num + 1}.png"
        text = pytesseract.image_to_string(Image.open(image_path))
        os.remove(image_path)

        current_part += text

        while len(current_part) >= gpt_limit:
            print(f"Part processed on {file}... ☑️")

            sliced = current_part[:gpt_limit]
            prompt_parts.append(sliced)
            current_part = current_part[gpt_limit:]

    prompt_parts.append(current_part)

# Init and end prompts, change if needed
init_prompt = f"""Hey! Can you make an exam with written questions out of these powerpoints? 
It's red through OCR so the data might look a little bit strange here and there, but focus on what seems important and relevant.

The total length of the content that I want to send you is too large to send in only one piece.
        
For sending you that content, I will follow this rule:
    
[START PART 1/{len(prompt_parts)}]
this is the content of the part 1 out of {len(prompt_parts)} in total
[END PART 1/{len(prompt_parts)}]
        
Then you just answer: "Received part 1/{len(prompt_parts)}"
        
And when I tell you "ALL PARTS SENT", then you can continue processing the data and answering my requests.
"""

end_prompt = "Create exam questions based on the information given"


# Adding parts for making GPT understand better
for i, part in enumerate(prompt_parts):
    prompt_parts[i] = (
        f"[START PART {i+1}/{len(prompt_parts)}]\n"
        + part
        + f"\n[END PART {i+1}/{len(prompt_parts)}]"
    )

# Generate prompts txts assuming prompts folder exist
with open("./prompts/0.txt", "w") as file:
    file.write(init_prompt)

for i, prompt in enumerate(prompt_parts):
    with open(f"./prompts/{i+1}.txt", "w") as file:
        file.write(prompt)

with open(f"./prompts/{len(prompt_parts)+1}.txt", "w") as file:
    file.write(end_prompt)

print(f"Done ✅")
