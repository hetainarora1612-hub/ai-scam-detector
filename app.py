import csv
import streamlit as st
from engine import analyze
from explain import highlight

st.set_page_config(page_title="AI Scam Detector", page_icon="🛡️")

st.title("🛡️ AI Scam Detector")
st.write("Paste a suspicious message below and I'll check it.")

st.sidebar.header("Try these examples")
st.sidebar.code("Your account is blocked. Share OTP now")
st.sidebar.code("Aapka SBI account band ho jayega. Abhi OTP share karein")
st.sidebar.code("You won Rs 25 lakh! Pay Rs 5000 fee at bit.ly/claim-now")
st.sidebar.code("Your Swiggy order is out for delivery")
st.sidebar.code("Your SBI OTP is 123456. Never share this with anyone")

text = st.text_area("Your message", height=150)

if st.button("Check", type="primary"):
    if text.strip() == "":
        st.warning("Please paste a message first.")
    else:
        r = analyze(text)
        pct = r["scam_percent"]

        if r["verdict"] == "SCAM":
            st.error(f"🚨 Likely SCAM ({pct}% scam chance)")
        elif r["verdict"] == "SUSPICIOUS":
            st.warning(f"⚠️ Suspicious ({pct}% scam chance). Be careful")
        else:
            st.success(f"✅ Looks safe ({pct}% scam chance)")

        st.markdown("**Your message, with risky words marked:**")
        st.markdown(highlight(text), unsafe_allow_html=True)

        if r["reasons"]:
            st.write("**Why it looks risky:**")
            for reason in r["reasons"]:
                st.write("- " + reason)

        if r["links"]:
            st.write("**Links found in this message:**")
            for item in r["links"]:
                st.write(f"🔗 `{item['link']}`")
                if item["warnings"]:
                    for w in item["warnings"]:
                        st.write("   - ⚠️ " + w)
                else:
                    st.write("   - Unknown link. Don't open it unless you trust the sender")

        st.caption(f"AI score: {r['ai_percent']}%  |  Rule signals found: {len(r['reasons'])}")

        if r["verdict"] != "SAFE":
            st.info(
                "**What should you do now?**\n\n"
                "- Do not click any link in this message\n"
                "- Never share your OTP, PIN or password with anyone\n"
                "- Call the cyber crime helpline **1930** if you lost money\n"
                "- Report at **cybercrime.gov.in**"
            )

# ---------- Report button ----------
st.divider()
st.write("**Did we miss a scam? Help improve the tool.**")
report_text = st.text_area("Paste the scam message here", key="report_box")
if st.button("Report this as scam"):
    if report_text.strip() == "":
        st.warning("Please paste a message to report.")
    else:
        with open("reported.csv", "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([report_text.strip(), 1])
        st.success("Thank you! The message was saved for review.")