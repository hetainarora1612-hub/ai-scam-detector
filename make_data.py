import os
import glob
import random
import string
import pandas as pd

random.seed(7)
PER_CLASS = 250_000          # 2.5 lakh scam + 2.5 lakh safe = 5 lakh

# ---------------- building blocks ----------------
BANKS = ["SBI", "HDFC", "ICICI", "Axis Bank", "PNB", "Bank of Baroda", "Kotak", "Canara Bank",
         "Union Bank", "Yes Bank", "IDFC First", "Indian Bank", "IndusInd", "Bank of India"]
WALLETS = ["Paytm", "PhonePe", "Google Pay", "BHIM", "Amazon Pay", "Mobikwik"]
COURIERS = ["FedEx", "India Post", "DHL", "BlueDart", "Delhivery", "Amazon", "Flipkart", "DTDC", "Ecom Express"]
SERVICES = ["Netflix", "Jio", "Airtel", "Vi", "FASTag", "LIC", "Amazon", "Hotstar", "Apple", "Google",
            "WhatsApp", "Instagram"]
GIFTS = ["iPhone 15", "Samsung phone", "laptop", "Rs 5000 voucher", "Amazon gift card", "bike", "Jio recharge"]
BIG = ["5 lakh", "10 lakh", "25 lakh", "50 lakh", "1 crore", "5 crore", "Rs 5,00,000", "Rs 25,00,000"]
SHOPS = ["Big Bazaar", "Reliance Fresh", "DMart", "Amazon", "Swiggy", "Zomato", "Petrol Pump", "Medplus",
         "Myntra", "Flipkart", "Blinkit", "Croma"]
NAMES = ["Rahul", "Priya", "Amit", "Sneha", "Ramesh", "Neha", "Vikram", "Pooja", "Mr Sharma", "Anjali",
         "Karan", "Divya", "Suresh", "Meena", "Arjun", "Kavita"]
DAYS = ["Monday", "Tuesday", "Friday", "Saturday", "Sunday", "15th", "20th", "25th", "28th", "1st", "10 October",
        "5 November"]
ACTS = ["match dekhne", "movie dekhne", "chai peene", "ghumne", "padhai karne", "cricket khelne"]
GOOD_LINKS = ["amazon.in/orders", "swiggy.com/track", "irctc.co.in", "meet.google.com/abc-defg-hij",
              "hdfcbank.com", "onlinesbi.sbi", "jio.com/recharge", "zoom.us/j/123456", "flipkart.com/orders"]
SHORT = ["bit.ly", "tinyurl.com", "cutt.ly", "t.co", "goo.gl", "bit.do"]
BRANDS = ["sbi", "hdfc", "icici", "axis", "pnb", "kotak", "paytm", "phonepe", "amazon", "flipkart", "jio",
          "airtel", "fastag", "aadhaar", "pan", "epfo", "irctc", "upi", "apple", "netflix"]
WORDS = ["verify", "update", "kyc", "login", "secure", "refund", "claim", "reward", "pay", "support", "care",
         "reactivate", "auth", "alert"]
BAD_TLDS = ["xyz", "top", "click", "link", "info", "icu", "buzz"]


def slug():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 8)))


def code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(5, 8)))


def bad_link():
    r = random.random()
    if r < 0.35:
        return f"{random.choice(SHORT)}/{slug()}"
    dom = f"{random.choice(BRANDS)}-{random.choice(WORDS)}.{random.choice(BAD_TLDS)}"
    if r < 0.60:
        return "http://" + dom
    if r < 0.70:
        return "https://" + dom + "/" + random.choice(WORDS)
    return dom


def phone():
    return f"{random.choice('6789')}{random.randint(0, 9)}XXXXXXXX"


def rs():
    n = random.choice([random.randint(10, 999), random.randint(1000, 99999),
                       random.choice([49, 99, 199, 299, 499, 999, 1500, 2000, 5000, 10000])])
    num = f"{n:,}" if random.random() < 0.3 else str(n)
    return random.choice(["Rs {}", "Rs. {}", "₹{}", "INR {}"]).format(num)


def promo_code():
    return random.choice(["WELCOME", "MEMBER", "SAVE10", "FESTIVE", "NEWUSER", "DIWALI"]) + \
        (str(random.randint(5, 50)) if random.random() < 0.5 else "")


def flight():
    return f"{random.choice(['6E', 'AI', 'UK', 'SG'])} {random.randint(100, 9999)}"


def slots():
    return dict(
        bank=random.choice(BANKS), wallet=random.choice(WALLETS), courier=random.choice(COURIERS),
        svc=random.choice(SERVICES), gift=random.choice(GIFTS), link=bad_link(),
        good_link=random.choice(GOOD_LINKS), phone=phone(), code=code(), rs=rs(), rs2=rs(),
        big=random.choice(BIG), shop=random.choice(SHOPS), name=random.choice(NAMES),
        otp=random.randint(100000, 999999), ref=random.randint(10**9, 10**10 - 1),
        n4=random.randint(1000, 9999), h=random.randint(1, 11),
        m=random.choice([5, 10, 15, 20, 30, 45]), day=random.choice(DAYS), promo=promo_code(),
        act=random.choice(ACTS), flight=flight(),
    )


def noise(s):
    """Small random changes so messages don't all look identical. Applied to both classes."""
    r = random.random()
    if r < 0.10:
        s = s.lower()
    elif r < 0.15:
        s = s.upper()
    elif r < 0.22:
        s = s.replace(".", "")
    return s.strip()


# ---------------- SCAM types: (claims, asks) ----------------
SCAM_TYPES = [
    # bank / KYC
    ([
        "Your {bank} KYC is pending", "Your {bank} account has been blocked",
        "Your {bank} account will be suspended", "Your {bank} debit card is blocked",
        "Your {bank} netbanking will expire today", "Unusual activity found on your {bank} account",
        "Aapka {bank} account band ho jayega", "Aapka {bank} KYC expire ho gaya hai",
        "Aapka {bank} ATM card block ho gaya hai", "Your {wallet} KYC has expired",
        "Your PAN card is blocked", "Your Aadhaar is suspended", "Your {bank} account is on hold",
    ], [
        "Update now at {link}", "Share OTP to avoid suspension", "Click {link} to verify",
        "Send card number and PIN to reactivate", "Verify your Aadhaar and PAN at {link}",
        "Download this app to update KYC: {link}", "Abhi OTP share karein",
        "Turant is link par click karein: {link}", "Call {phone} and share the OTP",
        "Enter card number and CVV at {link}", "Card number aur PIN bhejein turant",
    ]),
    # reward / lottery
    ([
        "You have won {big} in KBC lottery", "You won a {gift} in our lucky draw",
        "Aapne {big} ka inaam jeeta hai", "You are our 1000th visitor",
        "Cashback of {rs} is waiting for you", "You are selected for a free {gift} scheme",
        "Your reward points of {rs} will expire today", "Congratulations, you are the lucky winner of {big}",
        "Aapko lottery lagi hai",
    ], [
        "Pay {rs} fee to claim your prize", "Click {link} and enter your UPI PIN to claim",
        "Send your bank details to claim", "Pay {rs} GST to release the amount", "Share OTP to confirm",
        "Processing fee {rs} bhejein aur bank details dein", "Claim now at {link}",
        "Pay {rs} delivery charge to receive it",
    ]),
    # fake jobs
    ([
        "You are selected for a data entry job", "Part time job: earn {rs} per day rating hotels",
        "Work from home and earn {rs} daily", "Amazon HR here: earn {rs} daily by liking videos",
        "You have been selected for a remote task role", "Earn {rs} per week from your phone",
        "Aapka naukri ke liye selection ho gaya hai",
    ], [
        "Pay {rs} registration fee on UPI", "Deposit {rs} security amount to start",
        "Message me on Telegram now", "Reply YES to begin", "Join the task group: {link}",
        "Pay {rs} to activate your account", "Send Aadhaar and pay {rs} registration fee",
    ]),
    # fake police / government
    ([
        "This is CBI. A case is registered against you", "Your Aadhaar is linked to illegal activity",
        "Digital arrest: you are under investigation by police",
        "Income tax department final notice: arrest warrant issued",
        "RBI notice: your {bank} account is frozen due to suspicious activity",
        "A parcel in your name contains drugs. A customs officer will call you",
        "Your relative is in police custody", "Aapke naam par case darj hua hai",
    ], [
        "Pay {rs} fine now to avoid arrest", "Stay on video call and do not tell anyone",
        "Call officer on {phone} immediately", "Share Aadhaar and OTP to unfreeze",
        "Do not inform anyone and cooperate", "Send {rs} immediately to release him",
        "Pay {rs} now to cancel the warrant",
    ]),
    # delivery / customs
    ([
        "Your {courier} parcel could not be delivered", "Your {courier} package is held at customs",
        "Your {courier} package with tracking code {code} is waiting",
        "{courier}: illegal items found in your package", "Your parcel has been returned to the warehouse",
    ], [
        "Pay {rs} re-delivery fee at {link}", "Update your address now at {link} to avoid return",
        "Pay {rs} clearance fee at {link}", "Set delivery preference at {link}",
        "Talk to the customs officer now on {phone}",
    ]),
    # utility / toll / challan / SIM
    ([
        "Your electricity connection will be cut tonight", "You have an unpaid toll of {rs}",
        "You have a pending e-challan of {rs}", "Your FASTag is blocked",
        "Your gas connection will be stopped", "Your SIM will be deactivated in 2 hours",
        "Aapka bijli bill pending hai, aaj raat connection kat jayega", "Your {svc} bill is overdue",
    ], [
        "Call the officer on {phone} and pay immediately", "Avoid a late fee, pay at {link}",
        "Recharge now at {link} to avoid penalty", "Click {link} to verify",
        "Abhi is number par call karein: {phone}", "Pay {rs} to avoid disconnection",
    ]),
    # refund / UPI / collect request
    ([
        "You received a refund of {rs}", "Income tax refund of {rs} is pending",
        "I accidentally sent {rs} to your UPI", "{courier} is sending you a refund of {rs}",
        "Your {wallet} cashback of {rs} is pending", "{wallet} customer care: your payment failed",
        "Your {wallet} account will be blocked",
    ], [
        "Scan this QR code and enter your UPI PIN to receive", "Reply with your bank account number and IFSC",
        "Please send it back urgently on this UPI link: {link}", "Click {link} and enter bank details",
        "Call customer care on {phone}", "Install AnyDesk so we can fix it",
        "Scan this QR and enter PIN to verify",
    ]),
    # loan / investment / crypto
    ([
        "Instant personal loan up to {big}", "Invest {rs} and get {rs2} in one week",
        "Guaranteed 10x crypto returns", "Coinbase: amount received 2.2 BTC",
        "Our trading signals give 100 percent profit", "Loan approved instantly, no documents needed",
    ], [
        "Pay {rs} processing fee first", "Join our Telegram group now", "Confirm transaction at {link}",
        "Limited seats, join on WhatsApp", "Share Aadhaar and PAN and pay {rs} insurance first",
        "Send {rs} to this UPI ID to proceed",
    ]),
    # boss / family / code requests
    ([
        "Hi, I am your boss. I need your help urgently",
        "Bhai urgent paise chahiye, mera account freeze ho gaya hai",
        "Mera phone kharab ho gaya hai, ye naya number hai", "I sent you a 2FA code by mistake",
        "Hi, this is your CEO. I am in a meeting and cannot call", "Mom, I lost my phone, this is my new number",
    ], [
        "Buy gift cards worth {rs} and send me the codes", "Send {rs} immediately on this UPI link: {link}",
        "Send me the 6 digit code you received", "Do not tell anyone, just send {rs} now",
        "Message me on Telegram",
    ]),
    # tech account
    ([
        "Your Apple ID expires today", "Your Netflix subscription has expired",
        "Your WhatsApp will be deleted today", "Your Google account is suspended",
        "Your Instagram account violates our policy", "Your {svc} account is suspended",
    ], [
        "Log in at {link} to prevent deletion", "Verify by sending the 6 digit code you received",
        "Renew now at {link}", "Verify identity at {link} now", "Click {link} within 1 hour",
    ]),
]

URGENCY = ["", "", "", "Act today.", "Do it immediately.", "Within 2 hours.", "Last warning.", "Final notice.",
           "Valid for 24 hours only.", "Aaj hi karein.", "Turant karein.", "Abhi action lein.", "Do not delay.",
           "Offer expires tonight."]
COMMON = ["", "", "Dear customer, ", "Hello, ", "Hi, ", "{bank}: "]
SCAM_OPENERS = COMMON + ["URGENT: ", "Alert: ", "Dear user, ", "Sir, ", "Notice: ", "Congratulations! ",
                         "Aapka dhyan dein: ", "Final warning: "]

# ---------------- SAFE types: (templates, can_use_opener) ----------------
SAFE_TYPES = [
    ([
        "{rs} debited from your A/c XX{n4} at {shop}. Avl bal {rs2}",
        "{rs} credited to your account XX{n4}. Avl bal {rs2}",
        "UPI payment of {rs} to {name} successful. Ref no {ref}",
        "Your {bank} OTP is {otp}. Never share this with anyone, including bank staff",
        "Your OTP is {otp}. Do not share it with anyone. Valid for 10 minutes",
        "OTP {otp} for your transaction of {rs}. Do not share this OTP with anyone",
        "{bank}: {rs} spent on card ending {n4} at {shop}. Not you? Call the number on the back of your card",
        "Your credit card bill of {rs} is due on {day}. Pay through your bank app",
        "Your {bank} statement is ready. Login to the official app to view it",
        "Your bank will never ask for your OTP, PIN or CVV. Report fraud at cybercrime.gov.in or call 1930",
        "Warning: never share your OTP or password with anyone. {bank} never asks for them",
        "{rs} withdrawn from ATM. Avl bal {rs2}. Not you? Use the number on your card to contact your bank",
    ], True),
    ([
        "Thanks for your order! Your {shop} order #{ref} will be delivered by {day}",
        "Your {shop} order is out for delivery and will arrive in {m} minutes",
        "Your {courier} package with tracking code {code} is out for delivery today. Track it in the {courier} app",
        "Your order has shipped. Track it at {good_link}",
        "Your hotel booking is confirmed. Check-in code is {code}. Please show your ID at reception",
        "Your PNR is {code} for flight {flight} on {day}. Your e-ticket has been sent to your email",
        "Your cab booking is confirmed. Pickup at {h}:30 AM. Driver name {name}",
        "Your order #{ref} has been delivered. Rate your experience in the app",
        "Sorry, we had to reschedule your delivery. New date is {day}. Tracking code {code}",
    ], True),
    ([
        "Reminder: your appointment with Dr {name} is on {day} at {h} PM. Reply 1 to confirm or 2 to cancel",
        "Your weekly session is today at {h}:00. See you there",
        "Parent teacher meeting on Saturday at {h} AM in school",
        "Your library book is due tomorrow. Please return it on time",
        "Interview scheduled on {day} at {h} AM. Please bring your resume",
        "Your exam hall ticket is available on the college portal. Download it before {day}",
        "Meeting link for tomorrow's class: {good_link}",
        "Your subscription expires on {day}. Renew in the app. Reply STOP to unsubscribe",
        "Payment reminder: minimum due of {rs} on your card ending {n4} is payable by {day}",
        "Your electricity bill of {rs} is generated. Due date {day}. Pay via the official app",
    ], True),
    ([
        "Hi mom, I will reach home by {h}. Keep dinner ready",
        "Hey {name}, did you finish the report? Send it by tonight",
        "Bhai kal {act} chalein? Shaam ko {h} baje milte hain",
        "Happy birthday {name}! Wishing you a wonderful year ahead",
        "{name}, please send me the notes from class today",
        "Aaj raat khana bahar khate hain? {name}, tum bolo kahan chalein",
        "Meeting moved to {h} PM. Please join the same link as before",
        "Hi, are we meeting at {h} today?",
        "Thanks {name}, I got the money. Will pay you back on {day}",
        "Bhai paise bhej diye, check kar lena",
        "Papa, I reached the hostel safely. Will call in the evening",
        "Aapka order deliver ho gaya hai. Dhanyavaad",
    ], False),
    ([
        "Enjoy 10 percent off your next order at {shop}. Use code {promo}. Valid till {day}",
        "Our sale starts in 12 hours. Use code {promo} for early access. Reply STOP to opt out",
        "Thanks for stopping by {shop} today. How would you rate our service from 1 to 10?",
        "Your complaint with ticket {code} has been resolved. Thank you for your patience",
        "Thanks for joining our text club. Show this message at {shop} for a discount. Valid till {day}",
        "Your {svc} recharge of {rs} is successful. Validity 28 days",
        "Thank you for your payment of {rs}. Your receipt number is {ref}",
        "Dear {name}, thank you for your loyalty. Here is a {rs} voucher valid till {day}. Show this at the store",
    ], True),
]


def make_scam():
    claims, asks = random.choice(SCAM_TYPES)
    s = random.choice(SCAM_OPENERS) + random.choice(claims) + ". " + random.choice(asks)
    if random.random() < 0.6:
        s += ". " + random.choice(URGENCY)
    return noise(s.format(**slots()))


def make_safe():
    templates, use_opener = random.choice(SAFE_TYPES)
    s = random.choice(templates)
    if use_opener and random.random() < 0.4:
        s = random.choice(COMMON) + s
    return noise(s.format(**slots()))


def generate(fn, n):
    out, tries = set(), 0
    while len(out) < n and tries < n * 8:
        out.add(fn())
        tries += 1
    return list(out)


# ---------------- real-wording examples from your 3 documents ----------------
DOC_SCAMS = [
    "Congratulations! You have won a Rs 1000 Walmart gift card. Go to bit.ly/4kJp9x to claim now",
    "Your tax refund is pending acceptance. Must accept within 24 hours: bit.ly/sdfsdf",
    "Amazon is sending you a refund of Rs 3264. Please reply with your bank account number and IFSC to receive your refund",
    "SBI ALERT: Your account is temporarily locked. Please log in at goo.gl/2a234 to secure your account",
    "Hello, your FedEx package with tracking code DZ-8342-FY34 is waiting. Set delivery preference: c4lrs.info/Gm08s43zs1",
    "Hi Gary. This is your CEO. I need your help. Please buy 50 Amazon gift cards for the company party. Rs 1000 each",
    "Netflix: your subscription has expired. Renew now for just Rs 1 a month: 62jjsm4.eeaar.com",
    "OFFER FOR YOU. I can get you approved for a no interest credit card today ONLY. Learn more: aihfori.it.car.com",
    "Apple Notification. Your iCloud ID expires today. Log in to prevent deletion http://apple-id-auth.top/online",
    "Coinbase: Amount received 2.221 Bitcoin (Rs 15 lakh). Please confirm transaction: http://bit.do/Coinbase432194",
    "URGENT Your son was arrested last night. Need bail money immediately. Send Rs 95000 now http://goo.gl/ndf4g5",
    "Federal Credit Union ALERT: Your credit card has been temporarily LOCKED. Please call Card Services line 98XXXXXXXX",
    "Thank you for your recent Amazon purchase. You have been charged Rs 10834. If there is a mistake, please call 98XXXXXXXX",
    "Hi there. I need your help to pick up this package for me. Please see the order details here: afiaeoht80a.eta.ly",
    "I sent you a 2FA code from Craigslist. Send it to me when you can",
    "Toll Alert: You have an unpaid toll of Rs 325. Avoid a Rs 5000 late fee by settling today: sunpass-etc.com/pay",
    "Congrats! You have been selected for a remote task role. Earn Rs 2500 daily by rating apps and hotels. Reply YES to begin",
    "SBI ALERT: Your account will be blocked today. Verify immediately at bit.ly/sbi-verify to avoid suspension",
    "Congratulations! You have won Rs 4999 cashback. Click now to claim reward and complete UPI verification",
    "Dear customer, share your OTP immediately to stop account suspension. Failure to do so may block your banking access",
    "Your KYC is pending. Download secure banking app update here: short.link/update.apk",
    "Your parcel could not be delivered. Update your address now at bit.ly/delivery-fix to avoid return",
]
DOC_SAFE = [
    "Thanks for using promo code SAVE10. A 10 percent discount was applied to order A5124. Your backpack will arrive by 12 December",
    "Your hotel booking is confirmed. Check-in code is XYZ123 for room 123. Please show your ID at reception",
    "Your PNR is WE456 for flight EA2222 on Monday at 10:00. Your e-ticket has been sent to your email",
    "Hi Ravi, sorry we had to reschedule your shipping. New delivery date is 1 January, tracking code ABD458S",
    "Hello Meena, your complaint with ticket ABC215 has been resolved. Thank you for your patience",
    "Hello Barry, your quarterly gym subscription expires on 7 February. Renew at the front desk or in our app",
    "Hi Nick, a reminder about the Rs 750 minimum payment on your credit card ending 4521. Payment is due on 1 January",
    "Reminder: your appointment with Dr Brown is today at 2 PM. Please arrive 10 minutes early. Reply 1 to confirm or 2 to cancel",
    "Hi Diane, do not forget your appointment at Gracious Salon today at 4 PM. Call the salon if you have questions",
    "Thanks for stopping by today. We would love your feedback. How would you rate our service from 1 to 10?",
    "Our product launch is on 5 June. Text club members get 10 percent off. Reply STOP to unsubscribe",
    "Thanks for joining our text club. Show this message at the store for 10 percent off your next purchase. Valid till 5 May",
    "Hello Keith, we hope you are enjoying your blender. Please rate it in the app. It takes one minute",
    "Dear Marie, thank you for your loyalty. Here is a Rs 500 voucher valid till 10 October. Show this message at the store",
    "Report cyber fraud at cybercrime.gov.in or call 1930",
    "Your bank will never ask for your OTP, PIN or CVV on a call or SMS. Report fraud at cybercrime.gov.in",
]

# ---------------- assemble ----------------
hand = pd.read_csv("scam_data.csv")
hand["source"] = "hand"

docs = pd.DataFrame({"text": DOC_SCAMS + DOC_SAFE,
                     "label": [1] * len(DOC_SCAMS) + [0] * len(DOC_SAFE),
                     "source": "docs"})

print("Generating scam messages...")
scam_gen = generate(make_scam, PER_CLASS)
print("Generating safe messages...")
safe_gen = generate(make_safe, PER_CLASS)
gen = pd.DataFrame({"text": scam_gen + safe_gen,
                    "label": [1] * len(scam_gen) + [0] * len(safe_gen),
                    "source": "template"})

parts = [hand, docs, gen]

# Optional: your own extra CSV files in the extra_data folder
for path in glob.glob("extra_data/*.csv"):
    try:
        d = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        d = pd.read_csv(path, encoding="latin-1")
    d.columns = [c.strip().lower() for c in d.columns]
    d = d.rename(columns={"v1": "label", "v2": "text", "message": "text", "sms": "text", "category": "label"})
    d = d[["text", "label"]].copy()
    d["label"] = d["label"].astype(str).str.strip().str.lower().map(
        {"spam": 1, "scam": 1, "1": 1, "ham": 0, "safe": 0, "0": 0})
    d = d.dropna()
    d["label"] = d["label"].astype(int)
    d["source"] = "extra"
    parts.append(d)
    print("Added", path, "->", len(d), "messages")

# Optional: Kaggle SMS Spam file
if os.path.exists("spam.csv"):
    k = pd.read_csv("spam.csv", encoding="latin-1")[["v1", "v2"]]
    k.columns = ["label", "text"]
    k["label"] = k["label"].map({"ham": 0, "spam": 1})
    k["source"] = "kaggle"
    parts.append(k)
    print("Kaggle data added:", len(k))

big = pd.concat(parts, ignore_index=True)
big = big.drop_duplicates(subset="text").dropna()
big = big.sample(frac=1, random_state=1).reset_index(drop=True)
big.to_csv("big_data.csv", index=False, encoding="utf-8")

print("\nTotal saved in big_data.csv:", len(big))
print(big["source"].value_counts())
print(big["label"].value_counts())