# verso-content-manager - Diagramme Fonctionnel

> Genere par Forge. Regenerer: POST /api/skills/verso-content-manager/generate-diagram

## Diagramme

```mermaid
graph TD
    %% Subgraph Endpoints HTTP
    subgraph "Endpoints HTTP"
        health[/health]
        dashboard[/dashboard]
        articles[/articles]
        media[/media]
        seo[/seo]
        templates[/templates]
    end

    %% Subgraph Modules internes
    subgraph "Modules internes"
        fastapi[FastAPI App]
        dashboard_srv[Dashboard]
        articles_mod[Gestion Articles]
        media_mod[Gestion Media]
        seo_mod[Gestion SEO]
        templates_mod[Templates]
        wp_client[Client WP]
        vault[Vault Secrets]
        builder{{Builder JSON→HTML}}
        optimizer{{Optimiseur Image}}
    end

    %% Subgraph Dependances externes
    subgraph "Dependances externes"
        wp_api[WordPress API]
        onyx_vault[Onyx Vault]
        pillow[Pillow (Img)]
    end

    %% Connections Endpoints → FastAPI
    health --> fastapi
    dashboard --> dashboard_srv
    articles --> articles_mod
    media --> media_mod
    seo --> seo_mod
    templates --> templates_mod

    %% FastAPI routing
    fastapi --> dashboard_srv:::module
    fastapi --> articles_mod:::module
    fastapi --> media_mod:::module
    fastapi --> seo_mod:::module
    fastapi --> templates_mod:::module

    %% Articles flow
    articles_mod --> builder:::module
    builder --> wp_client:::module
    wp_client --> wp_api:::external

    %% Media flow
    media_mod --> optimizer:::module
    optimizer --> wp_client:::module
    optimizer --> pillow:::external

    %% SEO flow
    seo_mod --> wp_client:::module

    %% Templates usage
    templates_mod --> articles_mod:::module

    %% Vault usage
    vault --> wp_client:::module
    vault --> onyx_vault:::external

    %% Styles
    classDef endpoint fill:#4CAF50,stroke:#333,color:#fff;
    classDef module fill:#2196F3,stroke:#333,color:#fff;
    classDef external fill:#FF9800,stroke:#333,color:#fff;

    class health,dashboard,articles,media,seo,templates endpoint;
    class fastapi,dashboard_srv,articles_mod,media_mod,seo_mod,templates_mod,wp_client,vault,builder,optimizer module;
    class wp_api,onyx_vault,pillow external;
```
