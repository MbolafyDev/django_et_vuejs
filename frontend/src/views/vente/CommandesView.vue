<template>
  <div class="zs-root">
    <AppNavbar />

    <div class="container-fluid py-4 zs-admin">
      <!-- HEADER -->
      <div class="zs-hero mb-3">
        <div class="d-flex align-items-start justify-content-between flex-wrap gap-3">
          <div class="min-width-0">
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <div class="zs-dot"></div>
              <h4 class="mb-0 zs-title">Commandes</h4>
              <span class="zs-pill-soft">
                <i class="fa-solid fa-bolt me-1"></i> Vente & Livraison
              </span>
            </div>

            <!-- KPIs -->
            <div class="zs-kpis mt-3">
              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-list-check"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Résultats</div>
                  <div class="zs-kpi-value">{{ totalCount }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-regular fa-window-maximize"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Page</div>
                  <div class="zs-kpi-value">{{ page }} / {{ totalPages }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-layer-group"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Taille</div>
                  <div class="zs-kpi-value">{{ pageSize }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-tags"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Filtres</div>
                  <div class="zs-kpi-value">
                    <span v-if="hasActiveFilters" class="text-primary fw-bold">ON</span>
                    <span v-else class="text-muted">OFF</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- actions -->
          <div class="d-flex gap-2 flex-wrap align-items-center">
            <button class="btn btn-primary zs-btn zs-btn-neo" @click="openCreateModal" title="Nouvelle commande">
              <i class="fa-solid fa-plus"></i>
              <span class="ms-2 d-none d-sm-inline">Nouvelle</span>
            </button>

            <button class="btn btn-outline-secondary zs-btn zs-btn-neo" @click="refreshList" :disabled="loading" title="Rafraîchir">
              <i class="fa-solid fa-rotate"></i>
              <span class="ms-2 d-none d-sm-inline">Rafraîchir</span>
            </button>

            <button class="btn btn-outline-primary zs-btn zs-btn-neo" @click="toggleFilters" title="Filtres">
              <i class="fa-solid fa-filter me-1"></i>
              Filtres
              <span v-if="hasActiveFilters" class="zs-dot-mini ms-2"></span>
            </button>

            <button
              v-if="hasActiveFilters"
              class="btn btn-outline-danger zs-btn zs-btn-neo"
              @click="resetFiltersAndReload"
              title="Réinitialiser"
            >
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- ERROR -->
      <div v-if="error" class="alert alert-danger py-2">
        <i class="fa-solid fa-triangle-exclamation me-2"></i>{{ error }}
      </div>

      <!-- LIST -->
      <div class="zs-panel">
        <div class="zs-panel-head d-flex justify-content-between align-items-center gap-2 flex-wrap">
          <div class="d-flex align-items-center gap-2 min-width-0">
            <i class="fa-solid fa-list me-1 text-primary"></i>
            <span class="fw-bold">Liste des commandes</span>
            <span class="zs-pill-count">{{ totalCount }}</span>

            <div class="d-flex align-items-center gap-1 ms-2">
              <button class="btn btn-sm btn-outline-secondary zs-btn" @click="goPrev" :disabled="!prevUrl || loading" title="Précédent">
                <i class="fa-solid fa-chevron-left"></i>
              </button>
              <span class="small text-muted">Page {{ page }} / {{ totalPages }}</span>
              <button class="btn btn-sm btn-outline-secondary zs-btn" @click="goNext" :disabled="!nextUrl || loading" title="Suivant">
                <i class="fa-solid fa-chevron-right"></i>
              </button>

              <select v-model.number="pageSize" class="form-select form-select-sm ms-2 zs-input" style="width: 96px" title="Taille page">
                <option :value="10">10</option>
                <option :value="20">20</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
            </div>
          </div>

          <div class="d-flex align-items-center gap-2">
            <div class="btn-group btn-group-sm" role="group" aria-label="Affichage">
              <button class="btn zs-btn" :class="viewMode === 'table' ? 'btn-primary' : 'btn-outline-primary'" @click="viewMode = 'table'">
                <i class="fa-solid fa-table"></i>
              </button>
              <button class="btn zs-btn" :class="viewMode === 'card' ? 'btn-primary' : 'btn-outline-primary'" @click="viewMode = 'card'">
                <i class="fa-solid fa-id-card-clip"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- FILTERS -->
        <div v-if="showFilters" class="zs-filters px-3 pt-2 pb-3 border-top">
          <div class="row g-2">
            <div class="col-12 col-md-3">
              <label class="form-label small text-muted mb-1">Date commande</label>
              <input v-model="filters.date_commande" type="date" class="form-control form-control-sm zs-input" @change="applyFiltersServer" />
            </div>

            <div class="col-12 col-md-3">
              <label class="form-label small text-muted mb-1">Date livraison</label>
              <input v-model="filters.date_livraison" type="date" class="form-control form-control-sm zs-input" @change="applyFiltersServer" />
            </div>

            <div class="col-12 col-md-3">
              <label class="form-label small text-muted mb-1">Statut</label>
              <select v-model="filters.statut" class="form-select form-select-sm zs-input" @change="applyFiltersServer">
                <option value="">Tous</option>
                <option value="EN_ATTENTE">En attente</option>
                <option value="EN_LIVRAISON">En livraison</option>
                <option value="LIVREE">Livrée</option>
                <option value="ANNULEE">Annulée</option>
              </select>
            </div>

            <div class="col-12 col-md-3">
              <label class="form-label small text-muted mb-1">Client / Lieu</label>
              <input v-model="filters.client" class="form-control form-control-sm zs-input mb-2" placeholder="Nom client" @keyup.enter="applyFiltersServer" />
              <input v-model="filters.lieu" class="form-control form-control-sm zs-input" placeholder="Ex: Andraharo" @keyup.enter="applyFiltersServer" />
            </div>
          </div>

          <div class="mt-2 d-flex justify-content-end">
            <button class="btn btn-sm btn-primary zs-btn zs-btn-neo" @click="applyFiltersServer" :disabled="loading">
              <i class="fa-solid fa-magnifying-glass me-1"></i> Appliquer
            </button>
          </div>
        </div>

        <div class="zs-panel-body p-0">
          <div v-if="loading" class="p-3 text-muted">Chargement...</div>

          <!-- ✅ TABLE SIMPLE (SANS IMAGE, SANS ID, STYLE MINIMAL) -->
          <div v-else-if="viewMode === 'table'" class="p-3">
            <div v-if="!commandes.length" class="text-center text-muted py-4">
              <i class="fa-solid fa-circle-info me-1"></i> Aucun résultat
            </div>

            <div v-else class="zs-table-wrap">
              <table class="table table-sm align-middle zs-table-simple mb-0">
                <thead>
                  <tr>
                    <th>Date commande</th>
                    <th>Date livraison</th>
                    <th>Articles (client)</th>
                    <th>Page client</th>
                    <th>Statut</th>
                    <th class="text-end">Actions</th>
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="c in commandes" :key="c.id">
                    <td class="zs-td-date">
                      <div class="fw-semibold">{{ c.date_commande || "-" }}</div>
                      <div class="small text-muted">
                        <i class="fa-solid fa-user me-1"></i>{{ c.client_nom || "-" }}
                        <span v-if="c.client_contact"> • {{ c.client_contact }}</span>
                      </div>
                    </td>

                    <td class="zs-td-date">
                      <div class="fw-semibold">{{ c.date_livraison || "-" }}</div>
                      <div class="small text-muted">
                        <i class="fa-solid fa-location-dot me-1"></i>{{ c.lieu_detail?.nom || "-" }}
                        <span v-if="c.precision_lieu"> • {{ c.precision_lieu }}</span>
                      </div>
                    </td>

                    <td class="zs-td-articles">
                      <div v-if="c.lignes_detail?.length" class="zs-articles-list">
                        <div v-for="l in c.lignes_detail" :key="l.id" class="zs-article-line">
                          <span class="fw-semibold">{{ l.article_detail?.nom_produit || "Article" }}</span>
                          <span class="text-muted"> x{{ l.quantite }}</span>
                        </div>
                      </div>
                      <div v-else class="text-muted small">Aucun article</div>
                    </td>

                    <td class="zs-td-page">
                      <span v-if="c.page_detail?.nom" class="zs-tag">{{ c.page_detail.nom }}</span>
                      <span v-else class="text-muted">-</span>
                    </td>

                    <td class="zs-td-statut">
                      <span class="zs-status zs-status-sm" :class="badgeStatutClass(c.statut)">
                        <span class="zs-status-dot"></span>
                        <i class="fa-solid me-1" :class="iconStatut(c.statut)"></i>
                        {{ labelStatut(c.statut) }}
                      </span>
                    </td>

                    <td class="text-end">
                      <div class="d-inline-flex gap-2">
                        <button class="btn btn-sm btn-outline-primary zs-btn" @click="viewCommande(c)" title="Voir">
                          <i class="fa-solid fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning zs-btn" @click="openEditModal(c)" title="Éditer">
                          <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger zs-btn" @click="removeCommande(c.id)" title="Supprimer">
                          <i class="fa-solid fa-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- ✅ CARD (AVEC IMAGE ARTICLE) -->
          <div v-else class="p-3">
            <div v-if="!commandes.length" class="text-center text-muted py-4">
              <i class="fa-solid fa-circle-info me-1"></i> Aucun résultat
            </div>

            <div v-else class="zs-cards">
              <div v-for="c in commandes" :key="c.id" class="zs-cardline">
                <div class="d-flex justify-content-between align-items-start gap-3">
                  <!-- image article (card only) -->
                  <div class="zs-thumb zs-thumb-sm d-none d-sm-flex">
                    <img
                      v-if="firstArticlePhoto(c)"
                      :src="firstArticlePhoto(c)!"
                      alt="photo"
                    />
                    <i v-else class="fa-solid fa-box text-muted"></i>
                  </div>

                  <div class="min-width-0 flex-grow-1">
                    <div class="d-flex align-items-center gap-2 flex-wrap">
                      <div class="fw-bold">{{ c.client_nom || "Client" }}</div>
                      <span class="zs-status zs-status-sm" :class="badgeStatutClass(c.statut)">
                        <span class="zs-status-dot"></span>
                        <i class="fa-solid me-1" :class="iconStatut(c.statut)"></i>
                        {{ labelStatut(c.statut) }}
                      </span>
                    </div>

                    <div class="small text-muted zs-ellipsis mt-1" v-if="c.client_contact">
                      <i class="fa-solid fa-phone me-1"></i>{{ c.client_contact }}
                    </div>

                    <div class="small text-muted zs-ellipsis">
                      <i class="fa-regular fa-calendar me-1"></i> Cmd: {{ c.date_commande || "-" }}
                      <span v-if="c.date_livraison"> • <i class="fa-solid fa-truck me-1"></i>Liv: {{ c.date_livraison }}</span>
                    </div>

                    <div class="small text-muted zs-ellipsis">
                      <i class="fa-solid fa-location-dot me-1"></i> {{ c.lieu_detail?.nom || "-" }}
                      <span v-if="c.precision_lieu"> • {{ c.precision_lieu }}</span>
                    </div>

                    <div class="small text-muted zs-ellipsis" v-if="c.page_detail?.nom">
                      <i class="fa-regular fa-window-maximize me-1"></i> {{ c.page_detail.nom }}
                    </div>

                    <div class="mt-2">
                      <div v-if="c.lignes_detail?.length" class="d-flex flex-column gap-1">
                        <div v-for="l in c.lignes_detail" :key="l.id" class="small d-flex justify-content-between gap-2">
                          <div class="zs-ellipsis">
                            <span class="fw-semibold">{{ l.article_detail?.nom_produit || "Article" }}</span>
                            <span class="text-muted"> x{{ l.quantite }}</span>
                          </div>
                          <div class="text-muted">PU {{ formatAr(Number(l.prix_vente_unitaire)) }}</div>
                        </div>
                      </div>
                      <div v-else class="small text-muted">Aucun article</div>
                    </div>
                  </div>

                  <div class="text-end">
                    <div class="fw-bold">{{ formatAr(c.total_commande) }}</div>
                    <div class="small text-muted">{{ formatAr(c.total_articles) }} + {{ formatAr(c.frais_final || 0) }}</div>

                    <div class="mt-2 d-flex justify-content-end">
                      <div class="d-inline-flex gap-2">
                        <button class="btn btn-sm btn-outline-primary zs-btn" @click="viewCommande(c)" title="Voir">
                          <i class="fa-solid fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning zs-btn" @click="openEditModal(c)" title="Éditer">
                          <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger zs-btn" @click="removeCommande(c.id)" title="Supprimer">
                          <i class="fa-solid fa-trash"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- FOOTER -->
        <div class="zs-panel-foot border-top">
          <div class="small text-muted">
            {{ totalCount }} résultat(s) • Page {{ page }} / {{ totalPages }}
          </div>

          <div class="d-flex align-items-center gap-2">
            <button class="btn btn-sm btn-outline-secondary zs-btn" @click="goPrev" :disabled="!prevUrl || loading">
              <i class="fa-solid fa-chevron-left me-1"></i> Précédent
            </button>
            <button class="btn btn-sm btn-outline-secondary zs-btn" @click="goNext" :disabled="!nextUrl || loading">
              Suivant <i class="fa-solid fa-chevron-right ms-1"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL : VIEW -->
    <div v-if="showViewModal" class="modal fade show d-block zs-backdrop" tabindex="-1" @click.self="closeViewModal">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content zs-modal">
          <div class="modal-header">
            <h5 class="modal-title">Détails commande</h5>
            <button type="button" class="btn-close" @click="closeViewModal"></button>
          </div>

          <div class="modal-body">
            <div class="d-flex justify-content-between align-items-start gap-3">
              <div class="min-width-0">
                <div class="fw-bold">{{ selectedCommande?.client_nom }}</div>
                <div class="small text-muted" v-if="selectedCommande?.client_contact">{{ selectedCommande?.client_contact }}</div>

                <div class="small text-muted mt-2">
                  <i class="fa-regular fa-calendar me-1"></i>
                  Date commande: <b>{{ selectedCommande?.date_commande || "-" }}</b>
                </div>

                <div class="small text-muted" v-if="selectedCommande?.page_detail?.nom">
                  <i class="fa-regular fa-window-maximize me-1"></i>
                  Page: <b>{{ selectedCommande.page_detail.nom }}</b>
                </div>
              </div>

              <span class="zs-status zs-status-sm" :class="badgeStatutClass(selectedCommande?.statut)">
                <span class="zs-status-dot"></span>
                <i class="fa-solid me-1" :class="iconStatut(selectedCommande?.statut)"></i>
                {{ labelStatut(selectedCommande?.statut) }}
              </span>
            </div>

            <div class="mt-3">
              <div class="fw-bold">Livraison</div>
              <div class="small">
                <i class="fa-solid fa-location-dot me-1 text-muted"></i>
                {{ selectedCommande?.lieu_detail?.nom }}
              </div>
              <div class="small text-muted" v-if="selectedCommande?.precision_lieu">{{ selectedCommande?.precision_lieu }}</div>
              <div class="small" v-if="selectedCommande?.date_livraison">
                <i class="fa-solid fa-truck me-1 text-muted"></i>
                Date livraison: <b>{{ selectedCommande?.date_livraison }}</b>
              </div>
            </div>

            <hr />

            <div class="fw-bold mb-2">Articles</div>
            <div v-if="selectedCommande?.lignes_detail?.length" class="d-flex flex-column gap-2">
              <div v-for="l in selectedCommande.lignes_detail" :key="l.id" class="zs-line">
                <div class="d-flex gap-2 align-items-center">
                  <div class="zs-thumb">
                    <img v-if="l.article_detail?.photo_url" :src="l.article_detail.photo_url" alt="photo" />
                    <i v-else class="fa-solid fa-box text-muted"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="fw-semibold">{{ l.article_detail?.nom_produit }}</div>
                    <div class="small text-muted">
                      x{{ l.quantite }} • PU {{ formatAr(Number(l.prix_vente_unitaire)) }}
                      • Sous-total <b>{{ formatAr(Number(l.sous_total)) }}</b>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-muted">Aucun article</div>

            <hr />

            <div class="d-flex justify-content-between">
              <div>Total articles</div>
              <div class="fw-semibold">{{ formatAr(selectedCommande?.total_articles || 0) }}</div>
            </div>
            <div class="d-flex justify-content-between">
              <div>Frais livraison</div>
              <div class="fw-semibold">{{ formatAr(selectedCommande?.frais_final || 0) }}</div>
            </div>
            <div class="d-flex justify-content-between fs-5 mt-2">
              <div>Total à payer</div>
              <div class="fw-bold">{{ formatAr(selectedCommande?.total_commande || 0) }}</div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-outline-secondary zs-btn" @click="closeViewModal">Fermer</button>
            <button class="btn btn-warning zs-btn" @click="openEditModal(selectedCommande); closeViewModal()">
              <i class="fa-solid fa-pen-to-square me-1"></i> Éditer
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL : CREATE / EDIT -->
    <div v-if="showFormModal" class="modal fade show d-block zs-backdrop" tabindex="-1" @click.self="closeFormModal">
      <div class="modal-dialog modal-xl modal-dialog-scrollable">
        <div class="modal-content zs-modal">
          <div class="modal-header">
            <h5 class="modal-title">
              <span v-if="editingId">Éditer commande</span>
              <span v-else>Nouvelle commande</span>
            </h5>
            <button type="button" class="btn-close" @click="closeFormModal"></button>
          </div>

          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12 col-lg-5">
                <div class="zs-panel zs-panel-inner">
                  <div class="zs-panel-head d-flex align-items-center justify-content-between gap-2">
                    <div class="fw-bold min-width-0 zs-truncate">
                      <i class="fa-solid fa-file-invoice me-2 text-primary"></i>
                      {{ editingId ? `Éditer commande` : "Nouvelle commande" }}
                    </div>

                    <span v-if="editingId" class="zs-badge-warn">
                      <i class="fa-solid fa-pen-to-square me-1"></i> Édition
                    </span>
                    <span v-else class="zs-badge-ok">
                      <i class="fa-solid fa-circle-check me-1"></i> Prête
                    </span>
                  </div>

                  <div class="zs-panel-body">
                    <!-- Client -->
                    <div class="zs-field">
                      <label class="zs-label">Client *</label>
                      <div class="zs-control position-relative">
                        <div class="input-group input-group-sm">
                          <span class="input-group-text zs-ig">
                            <i class="fa-solid fa-user"></i>
                          </span>
                          <input
                            v-model="form.client_nom"
                            class="form-control zs-input"
                            placeholder="Tape le nom..."
                            @input="onClientInput"
                            @focus="onClientInput"
                            @keydown.enter.prevent="clientSuggestions[0] && selectClient(clientSuggestions[0])"
                            @keydown.down.prevent="clientSuggestions[0] && selectClient(clientSuggestions[0])"
                          />
                        </div>

                        <div v-if="clientSuggestions.length" class="zs-suggest list-group position-absolute w-100 shadow-sm mt-1">
                          <button
                            v-for="c in clientSuggestions"
                            :key="c.id"
                            type="button"
                            class="list-group-item list-group-item-action py-2"
                            @click="selectClient(c)"
                          >
                            <div class="d-flex justify-content-between">
                              <div class="fw-semibold">{{ c.nom }}</div>
                              <div class="small text-muted">{{ c.contact || "-" }}</div>
                            </div>
                          </button>
                        </div>

                        <div class="zs-help mt-1">
                          <span v-if="form.client_id" class="text-success">
                            <i class="fa-solid fa-circle-check me-1"></i> Client sélectionné
                          </span>
                          <span v-else class="text-muted">
                            <i class="fa-regular fa-floppy-disk me-1"></i> Si non trouvé, il sera enregistré automatiquement.
                          </span>
                        </div>
                      </div>
                    </div>

                    <!-- Contact -->
                    <div class="zs-field">
                      <label class="zs-label">Contact</label>
                      <div class="zs-control">
                        <div class="input-group input-group-sm">
                          <span class="input-group-text zs-ig"><i class="fa-solid fa-phone"></i></span>
                          <input v-model="form.client_contact" class="form-control zs-input" placeholder="Téléphone / email" />
                        </div>
                      </div>
                    </div>

                    <!-- Lieu -->
                    <div class="zs-field">
                      <label class="zs-label">Lieu *</label>
                      <div class="zs-control position-relative">
                        <div class="input-group input-group-sm">
                          <span class="input-group-text zs-ig"><i class="fa-solid fa-location-dot"></i></span>
                          <input
                            v-model="form.lieu_nom"
                            class="form-control zs-input"
                            placeholder="Tape le lieu..."
                            @input="onLieuInput"
                            @focus="onLieuInput"
                            @keydown.enter.prevent="lieuSuggestions[0] && selectLieu(lieuSuggestions[0])"
                            @keydown.down.prevent="lieuSuggestions[0] && selectLieu(lieuSuggestions[0])"
                          />
                        </div>

                        <div v-if="lieuSuggestions.length" class="zs-suggest list-group position-absolute w-100 shadow-sm mt-1">
                          <button
                            v-for="l in lieuSuggestions"
                            :key="l.id"
                            type="button"
                            class="list-group-item list-group-item-action py-2"
                            @click="selectLieu(l)"
                          >
                            <div class="d-flex justify-content-between align-items-start">
                              <div class="fw-semibold">{{ l.nom }}</div>
                              <span class="badge text-bg-light">{{ formatAr(l.default_frais) }}</span>
                            </div>
                            <div class="small text-muted">{{ l.categorie }}</div>
                          </button>
                        </div>

                        <div class="zs-help mt-1" v-if="form.lieu_id">
                          <i class="fa-solid fa-truck-fast me-1"></i>
                          Frais auto: <b>{{ formatAr(form.frais_auto || 0) }}</b>
                        </div>
                      </div>
                    </div>

                    <!-- Precision -->
                    <div class="zs-field">
                      <label class="zs-label">Précision</label>
                      <div class="zs-control">
                        <input v-model="form.precision_lieu" class="form-control form-control-sm zs-input" placeholder="Quartier, repère..." />
                      </div>
                    </div>

                    <!-- Date commande -->
                    <div class="zs-field">
                      <label class="zs-label">Date commande</label>
                      <div class="zs-control">
                        <input :value="todayISO" type="date" class="form-control form-control-sm zs-input" disabled />
                        <div class="zs-help mt-1"><i class="fa-regular fa-clock me-1"></i> Auto (created_at)</div>
                      </div>
                    </div>

                    <!-- Date livraison -->
                    <div class="zs-field">
                      <label class="zs-label">Date livraison</label>
                      <div class="zs-control">
                        <input v-model="form.date_livraison" type="date" class="form-control form-control-sm zs-input" />
                      </div>
                    </div>

                    <!-- Page -->
                    <div class="zs-field">
                      <label class="zs-label">Page</label>
                      <div class="zs-control">
                        <select v-model="form.page_id" class="form-select form-select-sm zs-input">
                          <option :value="null">— Aucune —</option>
                          <option v-for="p in pages" :key="p.id" :value="p.id">{{ p.nom }}</option>
                        </select>

                        <div class="zs-help mt-1 zs-ellipsis" v-if="selectedPage">
                          <i class="fa-regular fa-window-maximize me-1"></i>
                          <b class="zs-ellipsis d-inline-block" style="max-width: 100%">{{ selectedPage.nom }}</b>
                        </div>
                      </div>
                    </div>

                    <!-- Frais -->
                    <div class="zs-field">
                      <label class="zs-label">Frais</label>
                      <div class="zs-control">
                        <div class="input-group input-group-sm">
                          <span class="input-group-text zs-ig">Ar</span>
                          <input v-model.number="form.frais_override" type="number" class="form-control zs-input" placeholder="Vide = auto" />
                        </div>
                        <div class="zs-help mt-1">Frais appliqué: <b>{{ formatAr(fraisApplique) }}</b></div>
                      </div>
                    </div>

                    <!-- Totals -->
                    <div class="zs-totals mt-3">
                      <div class="d-flex justify-content-between">
                        <div>Total articles</div>
                        <div class="fw-semibold">{{ formatAr(totalArticlesLocal) }}</div>
                      </div>
                      <div class="d-flex justify-content-between">
                        <div>Livraison</div>
                        <div class="fw-semibold">{{ formatAr(fraisApplique) }}</div>
                      </div>
                      <hr class="my-2" />
                      <div class="d-flex justify-content-between align-items-center">
                        <div class="fw-semibold">Total à payer</div>
                        <div class="zs-total">{{ formatAr(totalCommandeLocal) }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- ARTICLES COLUMN -->
              <div class="col-12 col-lg-7">
                <div class="zs-panel zs-panel-inner">
                  <div class="zs-panel-head d-flex align-items-center justify-content-between">
                    <div class="fw-bold">
                      <i class="fa-solid fa-bag-shopping me-2 text-primary"></i> Articles
                    </div>
                    <span class="zs-pill-count">{{ form.lignes.length }}</span>
                  </div>

                  <div class="zs-panel-body">
                    <!-- add line -->
                    <div class="zs-addline mb-2 position-relative">
                      <div class="d-flex align-items-center gap-2 flex-wrap">
                        <div class="flex-grow-1 position-relative min-width-0">
                          <div class="input-group input-group-sm">
                            <span class="input-group-text zs-ig"><i class="fa-solid fa-magnifying-glass"></i></span>
                            <input
                              v-model="ligneDraft.query"
                              class="form-control zs-input"
                              placeholder="Produit / référence..."
                              @input="onArticleInput"
                              @focus="onArticleInput"
                            />
                          </div>

                          <div v-if="articleSuggestions.length" class="zs-suggest list-group position-absolute w-100 shadow-sm mt-1">
                            <button
                              v-for="a in articleSuggestions"
                              :key="a.id"
                              type="button"
                              class="list-group-item list-group-item-action py-2"
                              @click="selectArticleAndAutoAdd(a)"
                            >
                              <div class="d-flex gap-2 align-items-center">
                                <div class="zs-thumb zs-thumb-sm">
                                  <img v-if="a.photo_url" :src="a.photo_url" alt="photo" />
                                  <i v-else class="fa-solid fa-box text-muted"></i>
                                </div>

                                <div class="flex-grow-1 min-width-0">
                                  <div class="d-flex justify-content-between gap-2">
                                    <div class="fw-semibold text-truncate">{{ a.nom_produit }}</div>
                                    <div class="small text-muted">{{ formatAr(Number(a.prix_vente)) }}</div>
                                  </div>
                                  <div class="small text-muted text-truncate">
                                    Ref: {{ a.reference }} • Stock: {{ a.quantite_stock }}
                                  </div>
                                </div>
                              </div>
                            </button>
                          </div>
                        </div>

                        <div class="d-flex align-items-center gap-1 flex-shrink-0">
                          <button class="btn btn-sm btn-outline-secondary zs-btn" @click="ligneDraft.quantite = Math.max(1, (ligneDraft.quantite || 1) - 1)" title="-">
                            <i class="fa-solid fa-minus"></i>
                          </button>

                          <input
                            v-model.number="ligneDraft.quantite"
                            type="number"
                            min="1"
                            class="form-control form-control-sm text-center zs-input"
                            style="width: 72px"
                            title="Quantité"
                          />

                          <button class="btn btn-sm btn-outline-secondary zs-btn" @click="ligneDraft.quantite = (ligneDraft.quantite || 1) + 1" title="+">
                            <i class="fa-solid fa-plus"></i>
                          </button>
                        </div>
                      </div>

                      <div v-if="ligneDraft.article" class="zs-picked mt-2">
                        <div class="d-flex gap-2 align-items-center">
                          <div class="zs-thumb zs-thumb-sm">
                            <img v-if="ligneDraft.article?.photo_url" :src="ligneDraft.article.photo_url" alt="photo" />
                            <i v-else class="fa-solid fa-box text-muted"></i>
                          </div>
                          <div class="flex-grow-1 min-width-0">
                            <div class="d-flex justify-content-between gap-2">
                              <div class="fw-semibold text-truncate">{{ ligneDraft.article.nom_produit }}</div>
                              <div class="fw-bold">{{ formatAr(lineTotal) }}</div>
                            </div>
                            <div class="small text-muted text-truncate">
                              PU: <b>{{ formatAr(Number(ligneDraft.article.prix_vente)) }}</b> • Stock: {{ ligneDraft.article.quantite_stock }}
                            </div>
                            <div class="small text-muted">(Sélectionner dans la liste = ajout automatique)</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- lines -->
                    <div v-if="form.lignes.length" class="d-flex flex-column gap-2">
                      <div v-for="(l, i) in form.lignes" :key="i" class="zs-line">
                        <div class="d-flex gap-2 align-items-center">
                          <div class="zs-thumb">
                            <img v-if="l.photo_url" :src="l.photo_url" alt="photo" />
                            <i v-else class="fa-solid fa-box text-muted"></i>
                          </div>

                          <div class="flex-grow-1 min-width-0">
                            <div class="d-flex justify-content-between align-items-start gap-2">
                              <div class="min-width-0">
                                <div class="fw-semibold text-truncate">{{ l.nom_produit }}</div>
                                <div class="small text-muted text-truncate">Ref: {{ l.reference }}</div>
                              </div>

                              <button class="btn btn-sm btn-outline-danger zs-btn" @click="removeLigne(i)" title="Supprimer">
                                <i class="fa-solid fa-trash"></i>
                              </button>
                            </div>

                            <div class="d-flex justify-content-between align-items-center mt-2 flex-wrap gap-2">
                              <div class="d-flex align-items-center gap-1">
                                <button class="btn btn-sm btn-outline-secondary zs-btn" @click="decQty(i)" :disabled="l.quantite <= 1">
                                  <i class="fa-solid fa-minus"></i>
                                </button>
                                <span class="zs-pill-qty">x{{ l.quantite }}</span>
                                <button class="btn btn-sm btn-outline-secondary zs-btn" @click="incQty(i)">
                                  <i class="fa-solid fa-plus"></i>
                                </button>
                              </div>

                              <div class="text-end">
                                <div class="small text-muted">PU: {{ formatAr(Number(l.prix_vente_unitaire)) }}</div>
                                <div class="fw-bold">{{ formatAr(l.sous_total) }}</div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div v-else class="text-muted">
                      <i class="fa-solid fa-circle-info me-1"></i> Ajoute au moins 1 article.
                    </div>
                  </div>
                </div>

                <!-- actions -->
                <div class="d-grid mt-3">
                  <button class="btn btn-success zs-btn zs-btn-neo" @click="submit" :disabled="loading || !canSubmit">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="fa-solid" :class="editingId ? 'fa-pen-to-square' : 'fa-floppy-disk'"></i>
                    <span class="ms-2">{{ editingId ? "Mettre à jour" : "Enregistrer" }}</span>
                  </button>

                  <button v-if="editingId" class="btn btn-outline-secondary mt-2 zs-btn zs-btn-neo" @click="cancelEdit" :disabled="loading">
                    Annuler édition
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-outline-secondary zs-btn" @click="closeFormModal">Fermer</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import AppNavbar from "@/components/AppNavbar.vue";
import { VenteAPI, type ArticleSuggest, type ClientSuggest, type LieuSuggest, type PageOption } from "@/services/vente";

const loading = ref(false);
const error = ref("");

const commandes = ref<any[]>([]);
const totalCount = ref(0);
const nextUrl = ref<string | null>(null);
const prevUrl = ref<string | null>(null);

const page = ref(1);
const pageSize = ref(20);

const editingId = ref<number | null>(null);

// modals
const showViewModal = ref(false);
const selectedCommande = ref<any | null>(null);
const showFormModal = ref(false);

const viewMode = ref<"table" | "card">("table");

const showFilters = ref(false);
const filters = ref({
  date_commande: "" as string,
  date_livraison: "" as string,
  lieu: "" as string,
  client: "" as string,
  statut: "" as string,
});

function toggleFilters() { showFilters.value = !showFilters.value; }
function resetFilters() {
  filters.value = { date_commande: "", date_livraison: "", lieu: "", client: "", statut: "" };
}
const hasActiveFilters = computed(() => {
  const f = filters.value;
  return !!(f.date_commande || f.date_livraison || f.lieu.trim() || f.client.trim() || f.statut);
});

const totalPages = computed(() => Math.max(1, Math.ceil((totalCount.value || 0) / (pageSize.value || 1))));

function goNext() { if (!nextUrl.value) return; page.value += 1; loadCommandes(); }
function goPrev() { if (!prevUrl.value) return; page.value = Math.max(1, page.value - 1); loadCommandes(); }

function applyFiltersServer() { page.value = 1; loadCommandes(); }
function resetFiltersAndReload() { resetFilters(); page.value = 1; loadCommandes(); }
function refreshList() { loadCommandes(); }

// pages
const pages = ref<PageOption[]>([]);
const selectedPage = computed(() => {
  if (!form.value.page_id) return null;
  return pages.value.find((p) => p.id === form.value.page_id) || null;
});

async function loadPages() {
  try {
    const res = await VenteAPI.listPagesActives();
    pages.value = res.data || [];
  } catch (e) {
    console.warn("loadPages error:", e);
    pages.value = [];
  }
}

// today iso
const todayISO = computed(() => {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
});

// form
const form = ref({
  page_id: null as number | null,

  client_id: null as number | null,
  client_nom: "",
  client_contact: "",

  lieu_id: null as number | null,
  lieu_nom: "",
  frais_auto: 0,
  precision_lieu: "",

  date_livraison: "" as string,
  frais_override: null as number | null,

  lignes: [] as Array<{
    article: number;
    nom_produit: string;
    reference: string;
    quantite: number;
    prix_vente_unitaire: number;
    sous_total: number;
    photo_url?: string | null;
  }>,
});

const clientSuggestions = ref<ClientSuggest[]>([]);
const lieuSuggestions = ref<LieuSuggest[]>([]);
const articleSuggestions = ref<ArticleSuggest[]>([]);

let tClient: any = null;
let tLieu: any = null;
let tArticle: any = null;

const ligneDraft = ref({
  query: "",
  article: null as ArticleSuggest | null,
  quantite: 1,
});

const linePU = computed(() => Number(ligneDraft.value.article?.prix_vente || 0));
const lineTotal = computed(() => Math.round(linePU.value * (ligneDraft.value.quantite || 0)));
const canAddLine = computed(() => !!ligneDraft.value.article && (ligneDraft.value.quantite || 0) > 0);

function formatAr(v: number) {
  return `${Math.round(v || 0).toLocaleString("fr-FR")} Ar`;
}

const fraisApplique = computed(() => {
  if (form.value.frais_override !== null && form.value.frais_override !== undefined && form.value.frais_override !== ("" as any)) {
    return Number(form.value.frais_override) || 0;
  }
  return Number(form.value.frais_auto || 0);
});

const totalArticlesLocal = computed(() => form.value.lignes.reduce((s, l) => s + Number(l.sous_total || 0), 0));
const totalCommandeLocal = computed(() => totalArticlesLocal.value + fraisApplique.value);

const canSubmit = computed(() => {
  return !!form.value.client_nom.trim() && !!form.value.lieu_nom.trim() && form.value.lignes.length > 0;
});

// statut helpers
function labelStatut(s: any) {
  const map: any = {
    EN_ATTENTE: "En attente",
    EN_LIVRAISON: "En livraison",
    LIVREE: "Livrée",
    ANNULEE: "Annulée",
  };
  return map[s] || s || "-";
}
function badgeStatutClass(s: any) {
  switch (s) {
    case "EN_ATTENTE":   return "zs-st zs-st-neutral";
    case "EN_LIVRAISON": return "zs-st zs-st-ship";
    case "LIVREE":       return "zs-st zs-st-done";
    case "ANNULEE":      return "zs-st zs-st-cancel";
    default:             return "zs-st zs-st-neutral";
  }
}
function iconStatut(s: any) {
  switch (s) {
    case "EN_ATTENTE":   return "fa-hourglass-half";
    case "EN_LIVRAISON": return "fa-truck-fast";
    case "LIVREE":       return "fa-box-open";
    case "ANNULEE":      return "fa-circle-xmark";
    default:             return "fa-tag";
  }
}

// card helpers
function firstArticlePhoto(c: any): string | null {
  const photo = c?.lignes_detail?.[0]?.article_detail?.photo_url;
  return photo || null;
}

// qty helpers
function recalcLine(i: number) {
  const l = form.value.lignes[i];
  const q = Number(l.quantite || 0);
  const pu = Number(l.prix_vente_unitaire || 0);
  l.sous_total = Math.round(q * pu);
}
function incQty(i: number) { form.value.lignes[i].quantite += 1; recalcLine(i); }
function decQty(i: number) { if (form.value.lignes[i].quantite <= 1) return; form.value.lignes[i].quantite -= 1; recalcLine(i); }

// autosuggest
async function onClientInput() {
  clearTimeout(tClient);
  const q = form.value.client_nom.trim();
  form.value.client_id = null;

  if (!q) { clientSuggestions.value = []; return; }
  tClient = setTimeout(async () => {
    try {
      const res = await VenteAPI.suggestClients(q);
      clientSuggestions.value = res.data || [];
    } catch (e) {
      console.warn("suggestClients error:", e);
      clientSuggestions.value = [];
    }
  }, 200);
}

async function selectClient(c: ClientSuggest) {
  form.value.client_id = c.id;
  form.value.client_nom = c.nom;
  form.value.client_contact = c.contact || "";
  clientSuggestions.value = [];

  try {
    const res = await VenteAPI.getClientLastLieu(c.id);
    if (res.data) {
      form.value.lieu_id = res.data.lieu_id;
      form.value.lieu_nom = res.data.lieu_nom;
      form.value.frais_auto = Number(res.data.frais_auto || 0);

      if (!form.value.precision_lieu?.trim()) {
        form.value.precision_lieu = res.data.precision_lieu || "";
      }
      lieuSuggestions.value = [];
    }
  } catch (e) {
    console.warn("getClientLastLieu error:", e);
  }
}

async function onLieuInput() {
  clearTimeout(tLieu);
  const q = form.value.lieu_nom.trim();
  form.value.lieu_id = null;
  form.value.frais_auto = 0;

  if (!q) { lieuSuggestions.value = []; return; }
  tLieu = setTimeout(async () => {
    try {
      const res = await VenteAPI.suggestLieux(q);
      lieuSuggestions.value = res.data || [];
    } catch (e) {
      console.warn("suggestLieux error:", e);
      lieuSuggestions.value = [];
    }
  }, 200);
}

function selectLieu(l: LieuSuggest) {
  form.value.lieu_id = l.id;
  form.value.lieu_nom = l.nom;
  form.value.frais_auto = Number(l.default_frais || 0);
  lieuSuggestions.value = [];
}

async function onArticleInput() {
  clearTimeout(tArticle);
  const q = ligneDraft.value.query.trim();
  if (!q) {
    articleSuggestions.value = [];
    ligneDraft.value.article = null;
    return;
  }
  tArticle = setTimeout(async () => {
    try {
      const res = await VenteAPI.suggestArticles(q);
      articleSuggestions.value = res.data || [];
    } catch (e) {
      console.warn("suggestArticles error:", e);
      articleSuggestions.value = [];
    }
  }, 200);
}

function selectArticleAndAutoAdd(a: ArticleSuggest) {
  ligneDraft.value.article = a;
  ligneDraft.value.query = a.nom_produit;
  articleSuggestions.value = [];
  addLigne();
}

function addLigne() {
  if (!canAddLine.value) return;

  const a = ligneDraft.value.article!;
  const qte = Number(ligneDraft.value.quantite || 0);
  const pu = Number(a.prix_vente || 0);

  const idx = form.value.lignes.findIndex((x) => x.article === a.id);
  if (idx >= 0) {
    form.value.lignes[idx].quantite += qte;
    recalcLine(idx);
  } else {
    form.value.lignes.push({
      article: a.id,
      nom_produit: a.nom_produit,
      reference: a.reference,
      quantite: qte,
      prix_vente_unitaire: pu,
      sous_total: Math.round(qte * pu),
      photo_url: a.photo_url || null,
    });
  }
  ligneDraft.value = { query: "", article: null, quantite: 1 };
}

function removeLigne(i: number) { form.value.lignes.splice(i, 1); }

function resetForm() {
  editingId.value = null;
  form.value = {
    page_id: null,
    client_id: null,
    client_nom: "",
    client_contact: "",
    lieu_id: null,
    lieu_nom: "",
    frais_auto: 0,
    precision_lieu: "",
    date_livraison: "",
    frais_override: null,
    lignes: [],
  };
  clientSuggestions.value = [];
  lieuSuggestions.value = [];
  articleSuggestions.value = [];
  ligneDraft.value = { query: "", article: null, quantite: 1 };
}

function cancelEdit() { resetForm(); }

async function loadCommandes() {
  try {
    loading.value = true;
    error.value = "";

    const params: any = { page: page.value, page_size: pageSize.value };

    if (filters.value.date_livraison) params.date_livraison = filters.value.date_livraison;
    if (filters.value.date_commande) params.date_commande = filters.value.date_commande;
    if (filters.value.lieu.trim()) params.lieu = filters.value.lieu.trim();
    if (filters.value.client.trim()) params.client = filters.value.client.trim();
    if (filters.value.statut) params.statut = filters.value.statut;

    const res = await VenteAPI.list(params);

    commandes.value = res.data.results;
    totalCount.value = res.data.count;
    nextUrl.value = res.data.next;
    prevUrl.value = res.data.previous;
  } catch (e: any) {
    error.value = e?.response?.data ? JSON.stringify(e.response.data) : (e?.message || "Erreur");
  } finally {
    loading.value = false;
  }
}

function viewCommande(c: any) { selectedCommande.value = c; showViewModal.value = true; }
function closeViewModal() { showViewModal.value = false; selectedCommande.value = null; }

function openCreateModal() { resetForm(); showFormModal.value = true; }
function openEditModal(c: any) { if (!c) return; editCommande(c); showFormModal.value = true; }
function closeFormModal() { showFormModal.value = false; }

function editCommande(c: any) {
  editingId.value = c.id;

  form.value.page_id = c.page_detail?.id || c.page || null;

  form.value.client_id = c.client_detail?.id || null;
  form.value.client_nom = c.client_nom || "";
  form.value.client_contact = c.client_contact || "";

  form.value.lieu_id = c.lieu_detail?.id || null;
  form.value.lieu_nom = c.lieu_detail?.nom || "";
  form.value.frais_auto = Number(c.lieu_detail?.default_frais || 0);

  form.value.precision_lieu = c.precision_lieu || "";
  form.value.date_livraison = c.date_livraison || "";

  form.value.frais_override = null;

  form.value.lignes = (c.lignes_detail || []).map((l: any) => ({
    article: l.article,
    nom_produit: l.article_detail?.nom_produit || "",
    reference: l.article_detail?.reference || "",
    quantite: Number(l.quantite || 0),
    prix_vente_unitaire: Number(l.prix_vente_unitaire || 0),
    sous_total: Number(l.sous_total || 0),
    photo_url: l.article_detail?.photo_url || null,
  }));
}

async function submit() {
  try {
    loading.value = true;
    error.value = "";

    const payload = {
      page: form.value.page_id,
      precision_lieu: form.value.precision_lieu,
      date_livraison: form.value.date_livraison || null,
      frais_override: form.value.frais_override,

      client_input: form.value.client_id
        ? { id: form.value.client_id }
        : { nom: form.value.client_nom, contact: form.value.client_contact },

      lieu_input: form.value.lieu_id
        ? { id: form.value.lieu_id }
        : { nom: form.value.lieu_nom },

      lignes: form.value.lignes.map((l) => ({ article: l.article, quantite: l.quantite })),
    };

    if (editingId.value) await VenteAPI.update(editingId.value, payload as any);
    else await VenteAPI.create(payload as any);

    closeFormModal();
    resetForm();
    loadCommandes();
  } catch (e: any) {
    error.value = e?.response?.data ? JSON.stringify(e.response.data) : (e?.message || "Erreur");
  } finally {
    loading.value = false;
  }
}

async function removeCommande(id: number) {
  if (!confirm("Supprimer cette commande ?")) return;
  await VenteAPI.remove(id);
  if (commandes.value.length <= 1 && page.value > 1) page.value -= 1;
  loadCommandes();
}

function onPageSizeChange() { page.value = 1; loadCommandes(); }
watch(pageSize, () => onPageSizeChange());

onMounted(() => {
  loadPages();
  loadCommandes();
});
</script>

<style scoped>
.min-width-0 { min-width: 0; }
.zs-truncate { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.zs-ellipsis { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* backdrop */
.zs-backdrop { background: rgba(0,0,0,.45); }

.zs-admin{
  --zs-border: rgba(0,0,0,.08);
  --zs-border2: rgba(0,0,0,.06);
  --zs-shadow: 0 14px 34px rgba(0,0,0,.10);
  --zs-shadow-soft: 0 10px 20px rgba(0,0,0,.06);
  --zs-glass: rgba(255,255,255,.72);
  --zs-glass2: rgba(255,255,255,.88);
  --zs-ink: #0f172a;
  --zs-muted: rgba(15,23,42,.62);
  --zs-ring: rgba(13,110,253,.22);
}

.zs-root{
  background:
    radial-gradient(900px 360px at 20% 0%, rgba(13,110,253,.10), transparent 60%),
    radial-gradient(800px 320px at 90% 10%, rgba(25,135,84,.10), transparent 55%),
    radial-gradient(700px 300px at 50% 100%, rgba(220,53,69,.08), transparent 55%),
    #f7f8fb;
  min-height: 100vh;
}

/* hero */
.zs-hero{
  border: 1px solid var(--zs-border);
  border-radius: 22px;
  background: linear-gradient(135deg,
      rgba(13,110,253,.12),
      rgba(25,135,84,.07),
      rgba(255,255,255,.65)
    );
  box-shadow: var(--zs-shadow);
  padding: 16px 18px;
  backdrop-filter: blur(10px);
}
.zs-title{ color: var(--zs-ink); font-weight: 900; letter-spacing: .2px; }
.zs-dot{
  width: 12px; height: 12px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.9), rgba(13,110,253,1));
  box-shadow: 0 0 0 4px rgba(13,110,253,.12);
}
.zs-dot-mini{
  width: 8px; height: 8px;
  border-radius: 999px;
  background: rgba(13,110,253,1);
  box-shadow: 0 0 0 4px rgba(13,110,253,.12);
}
.zs-pill-soft{
  display:inline-flex;
  align-items:center;
  gap:.35rem;
  padding:.32rem .6rem;
  border-radius: 999px;
  border: 1px solid rgba(13,110,253,.18);
  background: rgba(255,255,255,.70);
  color: rgba(13,110,253,1);
  font-weight: 800;
  font-size: .78rem;
}

/* KPIs */
.zs-kpis{ display:flex; gap:10px; flex-wrap:wrap; }
.zs-kpi{
  display:flex; align-items:center; gap:.6rem;
  border: 1px solid var(--zs-border2);
  background: rgba(255,255,255,.70);
  border-radius: 16px;
  padding: 10px 12px;
  box-shadow: var(--zs-shadow-soft);
  backdrop-filter: blur(10px);
  min-width: 140px;
}
.zs-kpi-icon{
  width: 38px; height: 38px;
  border-radius: 14px;
  display:flex; align-items:center; justify-content:center;
  background: linear-gradient(180deg, rgba(13,110,253,.14), rgba(13,110,253,.04));
  border: 1px solid rgba(13,110,253,.16);
  color: rgba(13,110,253,1);
}
.zs-kpi-label{ font-size:.75rem; color: var(--zs-muted); line-height: 1.1; }
.zs-kpi-value{ font-size: 1.05rem; font-weight: 900; color: var(--zs-ink); }

/* panels */
.zs-panel{
  border-radius: 22px;
  border: 1px solid var(--zs-border);
  background: var(--zs-glass);
  box-shadow: var(--zs-shadow);
  overflow: hidden;
  backdrop-filter: blur(12px);
}
.zs-panel-inner{ box-shadow: none; border-radius: 18px; }
.zs-panel-head{
  padding: 12px 14px;
  background: var(--zs-glass2);
  border-bottom: 1px solid var(--zs-border);
}
.zs-panel-body{ padding: 14px; }
.zs-panel-foot{
  padding: 10px 12px;
  background: rgba(255,255,255,.78);
  display:flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

/* buttons */
.zs-btn{ border-radius: 14px; }
.zs-btn-neo{ box-shadow: 0 10px 18px rgba(0,0,0,.06); }

/* inputs */
.zs-ig{ background: rgba(255,255,255,.85) !important; }
.zs-input{ border-radius: 12px !important; }
.zs-input:focus{ box-shadow: 0 0 0 .2rem var(--zs-ring) !important; }

/* suggestions */
.zs-suggest{
  z-index: 60;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--zs-border);
}
.zs-suggest .list-group-item{ border: 0; }

/* thumbs */
.zs-thumb{
  width: 52px; height: 52px;
  border-radius: 14px;
  background: rgba(255,255,255,.75);
  border: 1px solid var(--zs-border);
  overflow: hidden;
  display:flex; align-items:center; justify-content:center;
  flex: 0 0 auto;
}
.zs-thumb img{ width: 100%; height: 100%; object-fit: cover; }
.zs-thumb-sm{ width: 40px; height: 40px; border-radius: 12px; }

/* tag */
.zs-tag{
  display:inline-flex;
  align-items:center;
  gap:.35rem;
  padding:.30rem .55rem;
  border-radius: 999px;
  border: 1px solid var(--zs-border);
  background: rgba(255,255,255,.80);
  font-weight: 800;
  font-size: .78rem;
  max-width: 100%;
}

/* ✅ STATUS: plus petit (pas grand) */
.zs-status{
  position: relative;
  display:inline-flex;
  align-items:center;
  gap:.35rem;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.08);
  white-space: nowrap;
}
.zs-status-dot{
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: currentColor;
  box-shadow: 0 0 0 3px rgba(255,255,255,.65);
}
/* taille réduite */
.zs-status-sm{
  padding: .22rem .55rem;
  font-weight: 900;
  font-size: .76rem;
  letter-spacing: .1px;
  box-shadow: 0 8px 14px rgba(0,0,0,.05);
}

.zs-st { color: #0f172a; background: rgba(255,255,255,.80); }
.zs-st-ship   { color:#a16207; background: linear-gradient(180deg, rgba(245,158,11,.22), rgba(255,255,255,.82)); border-color: rgba(245,158,11,.30); }
.zs-st-done   { color:#15803d; background: linear-gradient(180deg, rgba(34,197,94,.20), rgba(255,255,255,.82)); border-color: rgba(34,197,94,.28); }
.zs-st-cancel { color:#b91c1c; background: linear-gradient(180deg, rgba(239,68,68,.20), rgba(255,255,255,.82)); border-color: rgba(239,68,68,.28); }
.zs-st-neutral{ color:#334155; background: rgba(255,255,255,.80); }

/* ✅ TABLE SIMPLE */
.zs-table-wrap{
  border: 1px solid var(--zs-border);
  border-radius: 16px;
  overflow: hidden;
  background: rgba(255,255,255,.85);
}
.zs-table-simple thead th{
  font-size: .78rem;
  color: rgba(15,23,42,.70);
  font-weight: 900;
  background: rgba(248,249,250,.92);
  border-bottom: 1px solid var(--zs-border);
  padding: 10px 10px;
}
.zs-table-simple tbody td{
  padding: 10px 10px;
  border-top: 1px solid rgba(0,0,0,.06);
  vertical-align: top;
}
.zs-td-articles .zs-article-line{ line-height: 1.25; }
.zs-articles-list{ display:flex; flex-direction:column; gap:4px; }
.zs-td-date, .zs-td-page, .zs-td-statut { white-space: normal; }

/* cards list */
.zs-cards{ display:flex; flex-direction: column; gap: 10px; }
.zs-cardline{
  border: 1px solid var(--zs-border);
  background: rgba(255,255,255,.86);
  border-radius: 18px;
  padding: .85rem;
  box-shadow: var(--zs-shadow-soft);
}

/* modal */
.zs-modal{ border-radius: 18px; overflow: hidden; }

/* badges ok/warn */
.zs-badge-ok{
  display:inline-flex; align-items:center; gap:.35rem;
  padding:.25rem .6rem;
  border-radius: 999px;
  background: rgba(25,135,84,.12);
  border: 1px solid rgba(25,135,84,.22);
  color: rgba(25,135,84,1);
  font-weight: 900;
  font-size: .78rem;
}
.zs-badge-warn{
  display:inline-flex; align-items:center; gap:.35rem;
  padding:.25rem .6rem;
  border-radius: 999px;
  background: rgba(255,193,7,.14);
  border: 1px solid rgba(255,193,7,.28);
  color: rgba(120,90,0,1);
  font-weight: 900;
  font-size: .78rem;
}
</style>
