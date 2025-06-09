import streamlit as st
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from PIL import Image
import io

# Azure credentials
key = "9BdR5aI7R3hrYqslsmG0PGMBxyoMelXMuJKweuUP7abbb5B7PWmFJQQJ99BFACGhslBXJ3w3AAALACOGYcrt"
endpoint = "https://sreeraj.cognitiveservices.azure.com/"

# Create Azure client
client = FormRecognizerClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Streamlit UI
st.title("🧾 Receipt Analyzer with Azure Form Recognizer")
st.write("Upload a receipt image (JPG/PNG) to extract key details.")

uploaded_file = st.file_uploader("Upload your receipt", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Show uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Receipt", use_column_width=True)

    with st.spinner("Analyzing receipt..."):
        receipt_bytes = io.BytesIO()
        image.save(receipt_bytes, format="PNG")
        receipt_bytes.seek(0)

        poller = client.begin_recognize_receipts(receipt=receipt_bytes)
        result = poller.result()

        if result:
            receipt = result[0].fields

            st.subheader("📋 Receipt Details")

            st.write("**Merchant Address:**", receipt.get("MerchantAddress").value)
            st.write("**Contact Number:**", receipt.get("MerchantPhoneNumber").value)
            st.write("**Receipt Date:**", str(receipt.get("TransactionDate").value))
            st.write("**Tax Paid:**", receipt.get("Tax").value)
            st.write("**Total Amount Paid:**", receipt.get("Total").value)

            if "Items" in receipt:
                st.subheader("🛍️ Items Purchased")
                items_data = []

                for item_field in receipt["Items"].value:
                    item_details = item_field.value
                    items_data.append({
                        "Name": item_details.get("Name").value if "Name" in item_details else "",
                        "Price": item_details.get("Price").value if "Price" in item_details else "",
                        "Quantity": item_details.get("Quantity").value if "Quantity" in item_details else "",
                        "Total Price": item_details.get("TotalPrice").value if "TotalPrice" in item_details else "",
                    })

                st.table(items_data)
        else:
            st.error("No receipt data was extracted.")
