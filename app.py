import streamlit as st
from faster_whisper import WhisperModel
import re
import os

st.set_page_config(page_title="مساعد الاجتماعات الذكي", page_icon="🎙️")

st.title("🎙️ مساعد تلخيص الاجتماعات")
st.write("سجّل صوتك مباشرة وسيتم تحويله لنص واستخراج المهام تلقائيًا")

language_choice = st.radio("اختر لغة التسجيل:", ["العربية", "English"], horizontal=True)
lang_code = "ar" if language_choice == "العربية" else "en"

# تحميل نموذج faster-whisper مرة واحدة فقط (أخف بكثير من openai-whisper على الرام)
@st.cache_resource
def load_whisper_model():
    return WhisperModel("tiny", device="cpu", compute_type="int8")

model = load_whisper_model()

audio_value = st.audio_input("اضغط للتسجيل")

if audio_value is not None:
    st.audio(audio_value)

    with open("temp_audio.wav", "wb") as f:
        f.write(audio_value.getbuffer())

    if st.button("🚀 ابدأ التحليل"):
        with st.spinner("جاري تحويل الصوت لنص..."):
            try:
                segments, info = model.transcribe("temp_audio.wav", language=lang_code)
                text = " ".join([segment.text for segment in segments]).strip()

                st.subheader("📝 النص المستخرج:")
                st.write(text)

                def split_sentences(text, lang):
                    if lang == "ar":
                        trigger_words = "يجب|المسؤول|لازم|نتفق|نحتاج|نراجع|نحدّث|ننفذ|نطلق|يتكفل|يتابع|قرار|مطلوب|ضروري"
                        pattern = r"[.،,]|(?=و(?:" + trigger_words + r"))"
                    else:
                        trigger_words = "must|should|need to|has to|required|deadline|deploy|release|sprint|responsible for|decide|agreed to|assign"
                        pattern = r"[.,]|(?=\band\s+(?:" + trigger_words + r"))"
                    parts = re.split(pattern, text, flags=re.IGNORECASE)
                    return [p.strip() for p in parts if p and p.strip() != ""]

                def find_tasks(text, lang):
                    if lang == "ar":
                        task_keywords = [
                            "يجب", "على", "مطلوب", "لازم", "ضروري",
                            "نحتاج", "نراجع", "نحدّث", "ننفذ", "نطلق",
                            "المسؤول عن", "يتكفل", "يتابع",
                            "قرار", "نتفق على", "الموعد النهائي", "قبل يوم"
                        ]
                        owner_patterns = [
                            r"يجب على (\S+)",
                            r"المسؤول عن .+? هو (\S+)",
                            r"يتكفل (\S+)",
                            r"يتابع (\S+)",
                            r"هو (\S+)",
                            r"هي (\S+)"
                        ]
                    else:
                        task_keywords = [
                            "must", "should", "need to", "has to", "required",
                            "action item", "deadline", "deploy", "release",
                            "sprint", "bug", "follow up", "responsible for",
                            "decide", "agreed to", "due by", "assign"
                        ]
                        owner_patterns = [
                            r"responsible for .+? is (\S+)",
                            r"assign(?:ed)? to (\S+)",
                            r"(\S+) must",
                            r"(\S+) should"
                        ]

                    found_tasks = []
                    sentences = split_sentences(text, lang)
                    for sentence in sentences:
                        for keyword in task_keywords:
                            if keyword in sentence.lower():
                                owner = None
                                for pattern in owner_patterns:
                                    match = re.search(pattern, sentence, re.IGNORECASE)
                                    if match:
                                        owner = match.group(1).strip("،, ")
                                        break
                                found_tasks.append({"text": sentence, "owner": owner})
                                break
                    return found_tasks

                tasks = find_tasks(text, lang_code)
                st.subheader("✅ المهام المكتشفة:")
                if len(tasks) > 0:
                    for task in tasks:
                        if task["owner"]:
                            st.write(f"👤 **{task['owner']}** — {task['text']}")
                        else:
                            st.write("- " + task["text"])
                else:
                    st.write("لا توجد مهام واضحة بالنص")

                report_content = "النص المستخرج:\n" + text + "\n\n"
                report_content += "المهام المكتشفة:\n"
                if len(tasks) > 0:
                    for task in tasks:
                        if task["owner"]:
                            report_content += f"- [{task['owner']}] {task['text']}\n"
                        else:
                            report_content += "- " + task["text"] + "\n"
                else:
                    report_content += "لا توجد مهام واضحة بالنص\n"

                st.download_button(
                    label="⬇️ تحميل النتائج",
                    data=report_content.encode("utf-8"),
                    file_name="ملخص_الاجتماع.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"حدث خطأ أثناء تحويل الصوت: {e}")

            finally:
                if os.path.exists("temp_audio.wav"):
                    os.remove("temp_audio.wav")