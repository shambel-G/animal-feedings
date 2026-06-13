import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Animal Feeding Store",
    page_icon="🐾",
    layout="wide",
)

# ── Persistent storage helpers ────────────────────────────────────────────────
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def load(name):
    path = f"{DATA_DIR}/{name}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []

def save(name, data):
    with open(f"{DATA_DIR}/{name}.json", "w") as f:
        json.dump(data, f, indent=2)

# ── Session-state init ────────────────────────────────────────────────────────
for key in ["products", "customers", "suppliers", "sales"]:
    if key not in st.session_state:
        st.session_state[key] = load(key)

def persist(key):
    save(key, st.session_state[key])

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/emoji/96/paw-prints-emoji.png", width=80)
st.sidebar.title("🐾 Animal Feeding Store")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "📦 Inventory", "👥 Customers", "🚚 Suppliers", "🧾 Sales & Billing"],
)

# ══════════════════════════════════════════════════════════════════════════════
# 1. DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.title("🏠 Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    products  = st.session_state["products"]
    customers = st.session_state["customers"]
    suppliers = st.session_state["suppliers"]
    sales     = st.session_state["sales"]

    total_revenue = sum(s["total"] for s in sales)
    low_stock     = [p for p in products if p["qty"] < 10]

    c1.metric("Products",  len(products))
    c2.metric("Customers", len(customers))
    c3.metric("Suppliers", len(suppliers))
    c4.metric("Total Revenue", f"${total_revenue:,.2f}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚠️ Low Stock Alerts (< 10 units)")
        if low_stock:
            st.dataframe(
                pd.DataFrame(low_stock)[["name", "category", "qty", "price"]],
                use_container_width=True,
            )
        else:
            st.success("All products are sufficiently stocked.")

    with col2:
        st.subheader("🕒 Recent Sales")
        if sales:
            df = pd.DataFrame(sales).tail(5)[["date", "customer", "total"]]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No sales recorded yet.")

# ══════════════════════════════════════════════════════════════════════════════
# 2. INVENTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📦 Inventory":
    st.title("📦 Product / Inventory Management")
    products = st.session_state["products"]

    tab1, tab2 = st.tabs(["Product List", "Add / Edit Product"])

    with tab1:
        if products:
            df = pd.DataFrame(products)
            st.dataframe(df, use_container_width=True)

            st.markdown("#### Delete a Product")
            names = [p["name"] for p in products]
            to_del = st.selectbox("Select product to delete", names, key="del_prod")
            if st.button("🗑️ Delete Product"):
                st.session_state["products"] = [p for p in products if p["name"] != to_del]
                persist("products")
                st.success(f"'{to_del}' deleted.")
                st.rerun()
        else:
            st.info("No products yet. Add one in the next tab.")

    with tab2:
        st.subheader("Add or Update a Product")
        with st.form("product_form"):
            name     = st.text_input("Product Name")
            category = st.selectbox("Category", ["Dog Food", "Cat Food", "Bird Feed",
                                                  "Fish Feed", "Rabbit Feed", "Other"])
            qty      = st.number_input("Quantity in Stock", min_value=0, step=1)
            price    = st.number_input("Unit Price ($)", min_value=0.0, format="%.2f")
            supplier = st.text_input("Supplier Name")
            submitted = st.form_submit_button("💾 Save Product")

        if submitted:
            if not name:
                st.error("Product name is required.")
            else:
                existing = [p for p in products if p["name"].lower() == name.lower()]
                new_prod = {"id": len(products)+1, "name": name, "category": category,
                            "qty": qty, "price": price, "supplier": supplier}
                if existing:
                    st.session_state["products"] = [
                        new_prod if p["name"].lower() == name.lower() else p
                        for p in products
                    ]
                    st.success(f"'{name}' updated.")
                else:
                    st.session_state["products"].append(new_prod)
                    st.success(f"'{name}' added.")
                persist("products")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# 3. CUSTOMERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Customers":
    st.title("👥 Customer Management")
    customers = st.session_state["customers"]

    tab1, tab2 = st.tabs(["Customer List", "Add Customer"])

    with tab1:
        if customers:
            st.dataframe(pd.DataFrame(customers), use_container_width=True)
            st.markdown("#### Delete a Customer")
            names  = [c["name"] for c in customers]
            to_del = st.selectbox("Select customer", names, key="del_cust")
            if st.button("🗑️ Delete Customer"):
                st.session_state["customers"] = [c for c in customers if c["name"] != to_del]
                persist("customers")
                st.success(f"'{to_del}' deleted.")
                st.rerun()
        else:
            st.info("No customers yet.")

    with tab2:
        st.subheader("Register a New Customer")
        with st.form("cust_form"):
            name  = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            email = st.text_input("Email Address")
            pets  = st.text_input("Pet Types (e.g. Dog, Cat)")
            submitted = st.form_submit_button("➕ Add Customer")

        if submitted:
            if not name:
                st.error("Name is required.")
            else:
                st.session_state["customers"].append(
                    {"id": len(customers)+1, "name": name,
                     "phone": phone, "email": email, "pets": pets}
                )
                persist("customers")
                st.success(f"Customer '{name}' added.")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# 4. SUPPLIERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🚚 Suppliers":
    st.title("🚚 Supplier Management")
    suppliers = st.session_state["suppliers"]

    tab1, tab2 = st.tabs(["Supplier List", "Add Supplier"])

    with tab1:
        if suppliers:
            st.dataframe(pd.DataFrame(suppliers), use_container_width=True)
            st.markdown("#### Delete a Supplier")
            names  = [s["name"] for s in suppliers]
            to_del = st.selectbox("Select supplier", names, key="del_supp")
            if st.button("🗑️ Delete Supplier"):
                st.session_state["suppliers"] = [s for s in suppliers if s["name"] != to_del]
                persist("suppliers")
                st.success(f"'{to_del}' deleted.")
                st.rerun()
        else:
            st.info("No suppliers yet.")

    with tab2:
        st.subheader("Register a New Supplier")
        with st.form("supp_form"):
            name    = st.text_input("Supplier / Company Name")
            contact = st.text_input("Contact Person")
            phone   = st.text_input("Phone")
            email   = st.text_input("Email")
            product = st.text_input("Products Supplied")
            submitted = st.form_submit_button("➕ Add Supplier")

        if submitted:
            if not name:
                st.error("Supplier name is required.")
            else:
                st.session_state["suppliers"].append(
                    {"id": len(suppliers)+1, "name": name, "contact": contact,
                     "phone": phone, "email": email, "products": product}
                )
                persist("suppliers")
                st.success(f"Supplier '{name}' added.")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# 5. SALES & BILLING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧾 Sales & Billing":
    st.title("🧾 Sales & Billing")
    products  = st.session_state["products"]
    customers = st.session_state["customers"]
    sales     = st.session_state["sales"]

    tab1, tab2 = st.tabs(["New Sale", "Sales History"])

    with tab1:
        if not products:
            st.warning("Add products first (Inventory page).")
        elif not customers:
            st.warning("Add customers first (Customers page).")
        else:
            cust_names = [c["name"] for c in customers]
            customer   = st.selectbox("Customer", cust_names)

            prod_names  = [p["name"] for p in products]
            cart        = {}

            st.markdown("#### Add Items to Cart")
            with st.form("cart_form"):
                prod = st.selectbox("Product", prod_names)
                qty  = st.number_input("Quantity", min_value=1, step=1)
                add  = st.form_submit_button("➕ Add to Cart")

            if "cart" not in st.session_state:
                st.session_state.cart = {}

            if add:
                p_obj = next(p for p in products if p["name"] == prod)
                if qty > p_obj["qty"]:
                    st.error(f"Only {p_obj['qty']} units available.")
                else:
                    if prod in st.session_state.cart:
                        st.session_state.cart[prod]["qty"] += qty
                    else:
                        st.session_state.cart[prod] = {"qty": qty, "price": p_obj["price"]}
                    st.success(f"Added {qty} x {prod} to cart.")

            if st.session_state.cart:
                st.markdown("#### 🛒 Cart")
                rows  = [{"Product": k, "Qty": v["qty"], "Unit ($)": v["price"],
                           "Subtotal ($)": v["qty"]*v["price"]}
                          for k, v in st.session_state.cart.items()]
                total = sum(r["Subtotal ($)"] for r in rows)
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
                st.markdown(f"### Total: **${total:,.2f}**")

                col1, col2 = st.columns(2)
                if col1.button("✅ Confirm Sale"):
                    # Deduct stock
                    for name, info in st.session_state.cart.items():
                        for p in st.session_state["products"]:
                            if p["name"] == name:
                                p["qty"] -= info["qty"]
                    persist("products")

                    # Record sale
                    sale = {
                        "id": len(sales)+1,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "customer": customer,
                        "items": st.session_state.cart,
                        "total": total,
                    }
                    st.session_state["sales"].append(sale)
                    persist("sales")
                    st.session_state.cart = {}
                    st.success("Sale recorded successfully! 🎉")
                    st.rerun()

                if col2.button("🗑️ Clear Cart"):
                    st.session_state.cart = {}
                    st.rerun()

    with tab2:
        if sales:
            df = pd.DataFrame(
                [{"ID": s["id"], "Date": s["date"],
                  "Customer": s["customer"], "Total ($)": s["total"]}
                 for s in sales]
            )
            st.dataframe(df, use_container_width=True)
            st.markdown(f"### 💰 Grand Total Revenue: **${sum(s['total'] for s in sales):,.2f}**")

            st.markdown("#### View Sale Details")
            sale_id = st.selectbox("Select Sale ID", [s["id"] for s in sales])
            sale    = next(s for s in sales if s["id"] == sale_id)
            st.json(sale)
        else:
            st.info("No sales recorded yet.")
