HASURA_PROJECT_DIR=hasura
HASURA_ENDPOINT=http://localhost:8080
HASURA_ADMIN_SECRET=

hasura_export_metadata:
	cd $(HASURA_PROJECT_DIR) && \
	hasura metadata export --endpoint $(HASURA_ENDPOINT) \
	$(if $(HASURA_ADMIN_SECRET), --admin-secret $(HASURA_ADMIN_SECRET))
	git add $(HASURA_PROJECT_DIR)/metadata
	git commit -m "Update Hasura metadata"

hasura_apply_metadata:
	cd $(HASURA_PROJECT_DIR) && \
	hasura metadata apply --endpoint $(HASURA_ENDPOINT) \
	$(if $(HASURA_ADMIN_SECRET), --admin-secret $(HASURA_ADMIN_SECRET))

hasura_diff_metadata:
	cd $(HASURA_PROJECT_DIR) && \
	hasura metadata diff --endpoint $(HASURA_ENDPOINT) \
	$(if $(HASURA_ADMIN_SECRET), --admin-secret $(HASURA_ADMIN_SECRET))
