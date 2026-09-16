const providerData = {
  openrouter: { label: "OpenRouter", copy: "Automatic routing across many models, with an optional free tier.", provider: "openrouter", model: "openrouter/auto", key: "your-openrouter-key" },
  openai: { label: "OpenAI", copy: "Hosted OpenAI models with automatic fallback when configured.", provider: "openai", model: "gpt-4o-mini", key: "your-openai-key" },
  gemini: { label: "Gemini", copy: "Google AI Studio models for fast multimodal workflows.", provider: "gemini", model: "gemini-2.0-flash", key: "your-gemini-key" },
  anthropic: { label: "Claude", copy: "Anthropic models for careful reasoning and long context.", provider: "anthropic", model: "claude-3-5-sonnet-latest", key: "your-anthropic-key" },
  groq: { label: "Groq", copy: "Fast OpenAI-compatible inference through Groq.", provider: "groq", model: "llama-3.1-8b-instant", key: "your-groq-key" },
  ollama: { label: "Ollama", copy: "Private local inference on your machine. No API key required.", provider: "ollama", model: "llama3", key: "" }
};

let selectedProvider = "openrouter";
let wizardStep = 0;
const query = (selector) => document.querySelector(selector);

function copyText(text, button) {
  navigator.clipboard?.writeText(text);
  const original = button.textContent;
  button.textContent = "Copied";
  window.setTimeout(() => { button.textContent = original; }, 1300);
}

function renderProvider() {
  const provider = providerData[selectedProvider];
  query("#provider-summary").textContent = provider.copy;
  query("#provider-key").value = localStorage.getItem(`god-key-${selectedProvider}`) || "";
  query("#provider-model").value = provider.model;
  query("#provider-code").textContent = `from god_ai import aura\n\naura.configure(\n    provider="${provider.provider}",\n    api_key="${provider.key}",\n    model="${provider.model}",\n)`;
  document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.provider === selectedProvider));
}

const wizard = [
  ["Install a provider", "Install the core package with `python -m pip install god-ai`, then add a cloud extra or install Ollama locally."],
  ["Choose a model", "Use a provider model ID in the Model field. Ollama needs a model pulled with `ollama pull llama3`."],
  ["Configure Aura", "Copy the generated Python configuration or export AURA_PROVIDER, AURA_API_KEY, and AURA_MODEL in your shell."],
  ["Run a task", "Start with `god \"inspect this project\"` or call `aura.do()` from a Python program."],
];

function renderWizard() {
  const [title, description] = wizard[wizardStep];
  query("#wizard-panel").innerHTML = `<h3>${title}</h3><p>${description}</p>`;
  document.querySelectorAll("#wizard-list li").forEach((item, index) => item.classList.toggle("active", index === wizardStep));
  query("#previous").disabled = wizardStep === 0;
  query("#next").textContent = wizardStep === wizard.length - 1 ? "Restart" : "Next";
}

document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => {
  selectedProvider = tab.dataset.provider;
  renderProvider();
}));

query("#provider-key").addEventListener("input", (event) => localStorage.setItem(`god-key-${selectedProvider}`, event.target.value));
query("#provider-model").addEventListener("input", (event) => {
  providerData[selectedProvider].model = event.target.value;
  renderProvider();
});
query("#copy-config").addEventListener("click", (event) => copyText(query("#provider-code").textContent, event.currentTarget));
document.querySelectorAll("[data-copy]").forEach((button) => button.addEventListener("click", () => copyText(button.dataset.copy, button)));
query("#next").addEventListener("click", () => { wizardStep = (wizardStep + 1) % wizard.length; renderWizard(); });
query("#previous").addEventListener("click", () => { wizardStep = Math.max(0, wizardStep - 1); renderWizard(); });
query("#run-heal").addEventListener("click", () => { query("#heal-output").textContent = "1. captured RuntimeError: expected NCHW\n2. sent args and traceback to provider\n3. retry succeeded after shape normalization"; });
query("#run-parse").addEventListener("click", () => { query("#parse-output").textContent = 'input: "Ada is 36 years old"\nmodel: Person(name="Ada", age=36)\nstatus: validated'; });
query("#search-input").addEventListener("input", (event) => {
  const search = event.target.value.trim().toLowerCase();
  document.querySelectorAll("#api-list-wrap .api-list article").forEach((item) => {
    const matches = !search || (item.dataset.search || "").includes(search);
    item.classList.toggle("hidden", !matches);
  });
  document.querySelectorAll("#api-list-wrap .api-group").forEach((group) => {
    const visible = group.querySelectorAll(".api-list article:not(.hidden)").length > 0;
    group.style.display = visible ? "" : "none";
  });
});

document.querySelectorAll(".copy-code").forEach((button) => {
  button.addEventListener("click", () => {
    const codeBlock = button.parentElement.querySelector("pre code");
    if (codeBlock) copyText(codeBlock.textContent, button);
  });
});

query("#theme-toggle").addEventListener("click", () => {
  document.body.classList.toggle("light");
  localStorage.setItem("god-theme", document.body.classList.contains("light") ? "light" : "dark");
});

if (localStorage.getItem("god-theme") === "light") document.body.classList.add("light");
renderProvider();
renderWizard();
