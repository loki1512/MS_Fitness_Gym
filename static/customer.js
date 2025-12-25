import { dom } from "./dom.js";

export function initCustomerSection() {
  if (!dom.toggleCustomer) return;

  // Ensure initial state is hidden
  dom.customerFields.style.display = "none";

  dom.toggleCustomer.addEventListener("change", () => {
    if (dom.toggleCustomer.checked) {
      // ✅ Checkbox ON → show fields
      dom.customerFields.style.display = "block";
    } else {
      // ❌ Checkbox OFF → hide + clear
      dom.customerFields.style.display = "none";

      dom.customerName.value = "";
      dom.customerPhone.value = "";
      dom.customerAddress.value = "";
    }
  });
}
