(() => {
  const form = document.querySelector("[data-notes-form]");
  const editor = document.querySelector("[data-notes-editor]");
  if (!form || !editor) return;

  const hiddenBody = form.querySelector('input[name="body"]');
  const saveState = document.querySelector("[data-save-state]");
  const wordCount = document.querySelector("[data-word-count]");
  const saveButton = document.querySelector("[data-save-button]");
  const autosave = form.dataset.autosave === "true";
  let dirty = false;
  let submitting = false;
  let saving = false;
  let saveAgain = false;
  let revision = 0;
  let saveTimer;

  const updateWordCount = () => {
    const words = (editor.innerText || "").trim().split(/\s+/).filter(Boolean).length;
    wordCount.textContent = `${words} ${words === 1 ? "palavra" : "palavras"}`;
  };
  const queueAutosave = () => {
    if (!autosave || submitting) return;
    window.clearTimeout(saveTimer);
    saveState.textContent = "Salvando automaticamente…";
    saveTimer = window.setTimeout(saveNote, 850);
  };
  const setDirty = () => {
    dirty = true;
    revision += 1;
    saveState.textContent = autosave ? "Alterações pendentes…" : "Alterações ainda não salvas";
    saveButton.textContent = autosave ? "Salvar agora" : "Salvar nota";
    queueAutosave();
  };
  const saveNote = async () => {
    if (!autosave || !dirty || submitting) return;
    if (saving) {
      saveAgain = true;
      return;
    }
    saving = true;
    saveAgain = false;
    const sentRevision = revision;
    hiddenBody.value = editor.innerHTML;
    const data = new FormData(form);
    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: data,
        credentials: "same-origin",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error("save-failed");
      if (revision === sentRevision) {
        dirty = false;
        saveState.textContent = `Salvo às ${result.saved_at}`;
        saveButton.textContent = "Salvo";
      }
    } catch (_error) {
      saveState.textContent = "Não foi possível salvar. Clique em Salvar agora para tentar de novo.";
    } finally {
      saving = false;
      if (saveAgain || revision !== sentRevision) {
        saveAgain = false;
        queueAutosave();
      }
    }
  };

  const updateWordCountAndDirty = () => {
    setDirty();
    updateWordCount();
  };
  editor.addEventListener("input", updateWordCountAndDirty);
  form.querySelectorAll(".note-title-input, .note-topic-input").forEach((field) => field.addEventListener("input", setDirty));
  updateWordCount();

  form.querySelectorAll("[data-format]").forEach((button) => {
    button.addEventListener("mousedown", (event) => event.preventDefault());
    button.addEventListener("click", () => {
      editor.focus();
      document.execCommand(button.dataset.format, false, null);
      updateWordCountAndDirty();
    });
  });

  const highlightButton = form.querySelector("[data-highlight]");
  highlightButton.addEventListener("mousedown", (event) => event.preventDefault());
  highlightButton.addEventListener("click", () => {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed || !selection.rangeCount) return;
    const range = selection.getRangeAt(0);
    if (!editor.contains(range.commonAncestorContainer)) return;
    const selectedParent = range.commonAncestorContainer.nodeType === Node.ELEMENT_NODE
      ? range.commonAncestorContainer
      : range.commonAncestorContainer.parentElement;
    const existingMark = selectedParent?.closest("mark");
    if (existingMark && editor.contains(existingMark)) {
      const parent = existingMark.parentNode;
      while (existingMark.firstChild) parent.insertBefore(existingMark.firstChild, existingMark);
      parent.removeChild(existingMark);
    } else {
      const mark = document.createElement("mark");
      mark.appendChild(range.extractContents());
      range.insertNode(mark);
    }
    selection.removeAllRanges();
    updateWordCountAndDirty();
  });

  editor.addEventListener("paste", (event) => {
    event.preventDefault();
    const text = event.clipboardData?.getData("text/plain") || "";
    document.execCommand("insertText", false, text);
  });

  form.addEventListener("submit", (event) => {
    const deleteButton = event.submitter?.matches("[data-confirm-delete]");
    if (deleteButton && !window.confirm("Excluir esta nota? Essa ação não pode ser desfeita.")) {
      event.preventDefault();
      return;
    }
    window.clearTimeout(saveTimer);
    if (!deleteButton) hiddenBody.value = editor.innerHTML;
    submitting = true;
  });

  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
      event.preventDefault();
      if (autosave) {
        window.clearTimeout(saveTimer);
        saveNote();
      } else {
        hiddenBody.value = editor.innerHTML;
        submitting = true;
        form.requestSubmit(saveButton);
      }
    }
  });

  window.addEventListener("beforeunload", (event) => {
    if (dirty && !submitting) {
      event.preventDefault();
      event.returnValue = "";
    }
  });
})();
