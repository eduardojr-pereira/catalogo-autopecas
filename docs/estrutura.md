CATALOGO_AUTOPECAS/
│
│
├── data/
│   ├── raw/
│   ├── staging/
│   └── processed/
|
│
├── database/
│   ├── init/
│   │   ├── 00_init.sh
│   │   └── create_test_db.sql
│   │
│   ├── migrations/
│   │
│   ├── seeds/
│   │   ├── canonical_seed.sql
│   │   └── reference_seed.sql
│   │
│   ├── views/
│   │   ├── catalog_public_views.sql
│   │   └── catalog_search_views.sql
│   │
│   └── schema.sql
│
├── docker/
│   └── docker-compose.yml
│
├── docs/
│
├── src/
│   ├── catalog/
│   │   ├── application_service.py
│   │   ├── compatibility_service.py
│   │   ├── decision_service.py
│   │   ├── evidence_service.py
│   │   ├── inference_service.py
│   │   ├── part_service.py
│   │   ├── publication_service.py
│   │   ├── versioning_service.py
│   │   ├── fitment_service.py
│   │   └── search_service.py
│   │
│   ├── delivery/
│   │   ├── api/
│   │   │   ├── fitment_routes.py
│   │   │   ├── main.py
│   │   │   ├── publication_routes.py
│   │   │   ├── review_routes.py
│   │   │   └── search_routes.py
│   │   │
│   │   └── cli/
│   │       └── import_fipe.py
│   │
│   ├── ingestion/
│   │   ├── collectors/
│   │   │   └── fipe_api_collector.py
│   │   │
│   │   ├── loaders/
│   │   │   └── vehicle_reference_loader.py
│   │   │
│   │   ├── parsers/
│   │   │   └── fipe_parser.py
│   │   │
│   │   └── scrapers/   (vazio)
│   │
│   ├── processing/
│   │   ├── clustering/
│   │   │   └── cluster_service.py
│   │   │
│   │   ├── compatibility/
│   │   │   ├── compatibility_scorer.py
│   │   │   ├── fitment_rule_engine.py
│   │   │   └── rule_evaluator.py
│   │   │
│   │   ├── consolidation/
│   │   │   └── consolidation_service.py
│   │   │
│   │   ├── equivalence/
│   │   │   ├── equivalence_engine.py
│   │   │   ├── equivalence_loader.py
│   │   │   └── equivalence_scorer.py
│   │   │
│   │   └── normalization/
│   │       ├── code_normalizer.py
│   │       └── code_service.py
│   │
│   ├── reference/
│   │   ├── attribute_definition_service.py
│   │   ├── canonical_service.py
│   │   └── taxonomy_service.py
│   │
│   └── shared/
│       ├── config.py
│       ├── db.py
│       ├── enums.py
│       ├── logging_config.py
│       └── utils.py
│
├── tests/
│   ├── conftest.py
│   │
│   ├── fixtures/
│   │   └── fipe/
│   │       ├── brands.json
│   │       ├── models.json
│   │       └── years.json
│   │
│   ├── ingestion/
│   │   ├── test_fipe_collector.py
│   │   ├── test_fipe_parser.py
│   │   ├── test_import_fipe_cli.py
│   │   └── test_vehicle_reference_loader.py
│   │
│   ├── integration/
│   │   ├── test_bootstrap_database.py
│   │   ├── test_database.py
│   │   ├── test_fitment_service.py
│   │   ├── test_search_service.py
│   │   ├── test_compatibility_service.py
│   │   ├── test_publication_service.py
│   │   └── test_versioning_service.py
│   │
│   └── unit/
│       ├── test_equivalence_engine.py
│       ├── test_equivalence_scorer.py
│       ├── test_fitment_rule_engine.py
│       ├── test_normalizer.py
│       └── test_rule_evaluator.py
│
├── .pytest_cache/
├── .vscode/
├── venv/
├── .gitignore
├── README.md
└── requirements.txt