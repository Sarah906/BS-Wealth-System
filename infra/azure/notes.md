# Azure Deployment Notes

## Option A: Azure App Service + Azure Database for PostgreSQL

### Database
```bash
az postgres flexible-server create \
  --name wealthos-db \
  --resource-group wealthos-rg \
  --location saudiarabia \
  --admin-user wealthos \
  --admin-password YOUR_PASS \
  --sku-name Standard_B1ms \
  --tier Burstable
```

### Backend (App Service)
```bash
az webapp create \
  --resource-group wealthos-rg \
  --plan wealthos-plan \
  --name wealthos-backend \
  --deployment-container-image-name YOUR_ACR.azurecr.io/wealthos-backend:latest
```

### Frontend (Static Web App or App Service)
Next.js can be deployed to Azure Static Web Apps with API routes, or as a separate App Service.

## Option B: Azure Container Instances
Run the full docker-compose stack as container instances behind an Application Gateway.

## Secrets
Use Azure Key Vault:
```bash
az keyvault secret set --vault-name wealthos-kv --name "DATABASE-URL" --value "postgresql://..."
```
Reference in App Service settings using Key Vault references.

## Notes
- Saudi Arabia region: `saudiarabia` or `uaenorth` (closest)
- Use Azure Container Registry (ACR) for Docker image storage
- Enable Azure Monitor + Application Insights for logging
