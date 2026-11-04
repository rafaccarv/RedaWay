(() => {
  const root = document.documentElement;
  const themeSelects = document.querySelectorAll(".theme-select");
  const savedTheme = localStorage.getItem("redaway-theme");
  root.dataset.theme = savedTheme || "light";
  themeSelects.forEach((select) => {
    select.value = root.dataset.theme;
    select.addEventListener("change", () => {
      root.dataset.theme = select.value;
      localStorage.setItem("redaway-theme", select.value);
      themeSelects.forEach((other) => { other.value = select.value; });
    });
  });
  const planner = document.querySelector("#essay-planner");
  if (planner) {
    const preview = document.querySelector("#planner-preview");
    const title = document.querySelector("#planner-output-title");
    const printButton = document.querySelector("#planner-print");
    const fieldLabels = {
      thesis: "Tese",
      argument_one: "Argumento 1",
      argument_two: "Argumento 2",
      repertoire: "Referência ou evidência a verificar",
      agent: "Agente responsável",
      intervention: "Ação e modo de execução",
      goal: "Finalidade",
    };
    planner.addEventListener("submit", (event) => event.preventDefault());
    document.querySelector("#planner-submit").addEventListener("click", () => {
      const values = Object.fromEntries([...planner.querySelectorAll("[data-field]")].map((field) => [field.dataset.field, field.value]));
      const hasContent = Object.values(values).some((value) => String(value).trim());
      if (!hasContent) {
        title.textContent = "Adicione algumas ideias para montar o roteiro.";
        return;
      }
      title.textContent = values.theme.trim() || "Plano de redação";
      preview.replaceChildren();
      Object.entries(fieldLabels).forEach(([name, label]) => {
        const value = String(values[name] || "").trim();
        if (!value) return;
        const row = document.createElement("p");
        const heading = document.createElement("strong");
        heading.textContent = `${label}: `;
        row.append(heading, document.createTextNode(value));
        preview.append(row);
      });
      printButton.disabled = false;
    });
    document.querySelector("#planner-reset").addEventListener("click", () => {
      planner.reset();
      title.textContent = "As anotações vão aparecer aqui.";
      preview.replaceChildren();
      const message = document.createElement("p");
      message.textContent = "Comece pelo tema e pela tese. O roteiro é montado nesta página e não é enviado ao servidor nem salvo na conta.";
      preview.append(message);
      printButton.disabled = true;
    });
    printButton.addEventListener("click", () => window.print());
  }

  const sidebarButtons = document.querySelectorAll(".sidebar-collapse");
  const sidebarPreference = localStorage.getItem("redaway-sidebar-v2") === "collapsed";
  document.body.classList.toggle("sidebar-collapsed", sidebarPreference);
  sidebarButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(sidebarPreference));
    button.addEventListener("click", () => {
      const collapsed = document.body.classList.toggle("sidebar-collapsed");
      localStorage.setItem("redaway-sidebar-v2", collapsed ? "collapsed" : "expanded");
      sidebarButtons.forEach((control) => {
        control.setAttribute("aria-pressed", String(collapsed));
        control.setAttribute("aria-label", collapsed ? "Expandir navegação" : "Recolher navegação");
        control.title = collapsed ? "Expandir navegação" : "Recolher navegação";
      });
    });
  });
})();
