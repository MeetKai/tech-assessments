import { LitElement, html, nothing } from 'lit';
import { api, ApiError } from './api';
import '@fontsource/poppins/400.css';
import '@fontsource/poppins/500.css';
import '@fontsource/poppins/600.css';
import '@fontsource/poppins/700.css';
import './styles.css';

interface Document { id: number; title: string; summary: string; body: string; category_name: string; updated_at: string }
interface Results { items: Document[]; total: number; page: number; page_size: number }
interface Category { id: string; name: string }

export class KnowledgeApp extends LitElement {
  static properties = {
    token: {state: true}, query: {state: true}, category: {state: true}, page: {state: true},
    result: {state: true}, categories: {state: true}, error: {state: true}, busy: {state: true},
    selected: {state: true}, status: {state: true}, signingIn: {state: true},
  };
  token = sessionStorage.getItem('portal-token') || '';
  query = '';
  category = '';
  page = 1;
  result: Results | null = null;
  categories: Category[] = [];
  error: ApiError | null = null;
  busy = false;
  signingIn = false;
  selected: Document | null = null;
  status = 'Status desconhecido';
  private sequence = 0;
  private detailSequence = 0;

  createRenderRoot() { return this; }
  connectedCallback() {
    super.connectedCallback();
    if (this.token) void this.loadPortal();
  }

  private showError(error: unknown) {
    this.error = error instanceof ApiError ? error : new ApiError(0, 'Não foi possível concluir. Tente novamente.', 'indisponível');
    if (this.error.status === 401) this.signOut(false);
  }

  private async signIn(event: SubmitEvent) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget as HTMLFormElement);
    this.signingIn = true;
    this.error = null;
    try {
      const session = await api<{token: string}>('/login', '', {method: 'POST', body: JSON.stringify({username: fields.get('username'), password: fields.get('password')})});
      this.token = session.token;
      sessionStorage.setItem('portal-token', this.token);
      await this.loadPortal();
    } catch (error) { this.showError(error); }
    finally { this.signingIn = false; }
  }

  private signOut(clearError = true) {
    this.sequence++;
    this.detailSequence++;
    this.token = '';
    sessionStorage.removeItem('portal-token');
    this.result = null;
    this.selected = null;
    this.busy = false;
    this.query = '';
    this.category = '';
    this.page = 1;
    if (clearError) this.error = null;
  }

  private async loadPortal() {
    try {
      this.categories = await api<Category[]>('/categories', this.token);
      await this.search();
    } catch (error) { this.showError(error); }
  }

  private async search() {
    const sequence = ++this.sequence;
    this.busy = true;
    this.error = null;
    this.selected = null;
    this.detailSequence++;
    const params = new URLSearchParams({q: this.query, page: String(this.page), category: this.category});
    try {
      const result = await api<Results>(`/search?${params}`, this.token);
      if (sequence === this.sequence) this.result = result;
    } catch (error) {
      if (sequence === this.sequence) { this.result = null; this.showError(error); }
    } finally { if (sequence === this.sequence) this.busy = false; }
  }

  private queryChanged(event: Event) {
    this.query = (event.target as HTMLInputElement).value;
    this.page = 1;
    void this.search();
  }

  private async openDocument(id: number) {
    const sequence = ++this.detailSequence;
    try {
      const document = await api<Document>(`/documents/${id}`, this.token);
      if (sequence === this.detailSequence) this.selected = document;
    } catch (error) { if (sequence === this.detailSequence) this.showError(error); }
  }

  private errorView() {
    if (!this.error) return nothing;
    return html`<aside class="error" role="alert"><strong>Não foi possível continuar</strong><p>${this.error.status === 403 ? 'Você não tem permissão para acessar este recurso.' : this.error.message}</p><div class="error-meta"><span>${this.error.status ? `HTTP ${this.error.status}` : 'Sem resposta HTTP'}</span><span>Código de atendimento: <code>${this.error.requestId}</code></span></div></aside>`;
  }

  render() {
    return html`
      <header class="topbar"><a class="wordmark" href="/" aria-label="MeetKai Brasil, início"><strong>meetkai</strong><span>brasil</span></a><div class="header-end"><span class="status" role="status"><i class=${this.status === 'Operacional' ? 'online' : this.status === 'Instável' ? 'unstable' : ''}></i>${this.status}</span>${this.token ? html`<button class="text-button" @click=${() => this.signOut()}>Sair</button>` : nothing}</div></header>
      <main>
      ${!this.token ? html`
        <div class="login-layout">
          <section class="intro"><span class="eyebrow">PORTAL DE CONSULTA</span><h1><strong>Conhecimento</strong><span>para o dia a dia.</span></h1><p>Encontre orientações e documentos para apoiar o seu trabalho.</p><div class="bookmarks" aria-hidden="true"><span></span><span></span><span></span></div><p class="demo-note">Ambiente de demonstração<br>Conteúdo e contas fictícios.</p></section>
          <section class="login-panel"><span class="eyebrow">BASE DE CONHECIMENTO</span><h2>Acesse sua conta</h2><p>Entre para consultar o acervo.</p>${this.errorView()}<form @submit=${this.signIn}><label for="username">Usuário</label><input id="username" name="username" autocomplete="username" required><label for="password">Senha</label><input id="password" name="password" type="password" autocomplete="current-password" required><button class="primary" type="submit" ?disabled=${this.signingIn}>${this.signingIn ? 'Entrando…' : 'Entrar'}<span aria-hidden="true">↗</span></button></form><p class="login-help">Precisa de acesso? Procure a pessoa responsável pelo portal.</p></section>
        </div>
      ` : html`
        <section class="search-heading"><div><span class="eyebrow">BASE DE CONHECIMENTO</span><h1><strong>Encontre respostas.</strong><span>Continue seu trabalho.</span></h1></div><p>Orientações, procedimentos e referências<br>em um só lugar.</p></section>
        <form class="search-form" @submit=${(e: Event) => { e.preventDefault(); void this.search(); }}><div class="search-field"><label for="query">O que você procura?</label><div class="input-wrap"><span aria-hidden="true">⌕</span><input id="query" type="search" maxlength="200" placeholder="Busque por assunto ou palavra-chave" .value=${this.query} @input=${this.queryChanged}></div></div><div class="category-field"><label for="category">Categoria</label><select id="category" .value=${this.category} @change=${(e: Event) => { this.category = (e.target as HTMLSelectElement).value; this.page = 1; void this.search(); }}><option value="">Todas as categorias</option>${this.categories.map(c => html`<option value=${c.id}>${c.name}</option>`)}</select></div><button type="submit" class="primary search-button">Buscar <span aria-hidden="true">↗</span></button></form>
        ${this.errorView()}
        ${this.selected ? html`<section class="document-detail"><button class="text-button" @click=${() => { this.selected = null; this.detailSequence++; }}>← Voltar aos resultados</button><span class="category-tag">${this.selected.category_name}</span><h2>${this.selected.title}</h2><p>${this.selected.body}</p></section>` : html`
          <section class="results" aria-busy=${this.busy}><div class="results-heading"><h2>Acervo de documentos</h2><span role="status">${this.busy ? 'Consultando…' : this.result ? `${this.result.total} documentos encontrados` : 'Consulta indisponível'}</span></div>
          ${this.result?.items.map(doc => html`<article class="document-row"><span class="document-symbol" aria-hidden="true">▤</span><div><span class="category-tag">${doc.category_name}</span><h3><button class="document-link" @click=${() => this.openDocument(doc.id)}>${doc.title}</button></h3><p>${doc.summary}</p></div><span class="row-arrow" aria-hidden="true">↗</span></article>`)}
          ${this.result?.total === 0 ? html`<p class="empty">Nenhum documento encontrado. Tente outro termo ou escolha outra categoria.</p>` : nothing}
          ${this.result && this.result.total > 0 ? html`<nav class="pagination" aria-label="Páginas de resultados"><span>Página ${this.page} de ${Math.max(1, Math.ceil(this.result.total / this.result.page_size))}</span><div><button ?disabled=${this.page <= 1 || this.busy} @click=${() => { this.page--; void this.search(); }}>← Anterior</button><button ?disabled=${this.page * this.result.page_size >= this.result.total || this.busy} @click=${() => { this.page++; void this.search(); }}>Próxima →</button></div></nav>` : nothing}</section>
        `}
      `}
      </main><footer><span>Base de Conhecimento</span><span>MeetKai Brasil · Ambiente de demonstração</span></footer>
    `;
  }
}
customElements.define('knowledge-app', KnowledgeApp);
