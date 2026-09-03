import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.AudioFile("audio.wav") as source:
    audio_data = recognizer.record(source)

try:
    text = recognizer.recognize_google(audio_data, language="ar-SA")
    print("النص المستخرج:")
    print(text)
    print("---")

    words = text.split()
    print("عدد الكلمات:", len(words))

    def find_tasks(text):
        task_keywords = ["يجب", "على", "مطلوب", "لازم", "ضروري"]
        found_tasks = []
        sentences = text.split(".")
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence == "":
                continue
            for keyword in task_keywords:
                if keyword in sentence:
                    if sentence not in found_tasks:
                        found_tasks.append(sentence)
                    break

        return found_tasks

    tasks = find_tasks(text)
    print("المهام المكتشفة:")
    if len(tasks) > 0:
        for task in tasks:
            print("-", task)
    else:
        print("لا توجد مهام واضحة بالنص")

except sr.UnknownValueError:
    print("لم أستطع فهم الصوت بوضوح")
except sr.RequestError:
    print("خطأ في الاتصال بخدمة التعرف على الصوت")