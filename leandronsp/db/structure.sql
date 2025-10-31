CREATE TABLE IF NOT EXISTS "schema_migrations" ("version" varchar NOT NULL PRIMARY KEY);
CREATE TABLE IF NOT EXISTS "ar_internal_metadata" ("key" varchar NOT NULL PRIMARY KEY, "value" varchar, "created_at" datetime(6) NOT NULL, "updated_at" datetime(6) NOT NULL);
CREATE TABLE IF NOT EXISTS "active_storage_blobs" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "key" varchar NOT NULL, "filename" varchar NOT NULL, "content_type" varchar, "metadata" text, "service_name" varchar NOT NULL, "byte_size" bigint NOT NULL, "checksum" varchar, "created_at" datetime(6) NOT NULL);
CREATE UNIQUE INDEX "index_active_storage_blobs_on_key" ON "active_storage_blobs" ("key") /*application='Macedo'*/;
CREATE TABLE IF NOT EXISTS "active_storage_attachments" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "name" varchar NOT NULL, "record_type" varchar NOT NULL, "record_id" bigint NOT NULL, "blob_id" bigint NOT NULL, "created_at" datetime(6) NOT NULL, CONSTRAINT "fk_rails_c3b3935057"
FOREIGN KEY ("blob_id")
  REFERENCES "active_storage_blobs" ("id")
);
CREATE INDEX "index_active_storage_attachments_on_blob_id" ON "active_storage_attachments" ("blob_id") /*application='Macedo'*/;
CREATE UNIQUE INDEX "index_active_storage_attachments_uniqueness" ON "active_storage_attachments" ("record_type", "record_id", "name", "blob_id") /*application='Macedo'*/;
CREATE TABLE IF NOT EXISTS "active_storage_variant_records" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "blob_id" bigint NOT NULL, "variation_digest" varchar NOT NULL, CONSTRAINT "fk_rails_993965df05"
FOREIGN KEY ("blob_id")
  REFERENCES "active_storage_blobs" ("id")
);
CREATE UNIQUE INDEX "index_active_storage_variant_records_uniqueness" ON "active_storage_variant_records" ("blob_id", "variation_digest") /*application='Macedo'*/;
CREATE VIRTUAL TABLE dishes_fts USING fts5(
  name,
  description,
  dish_type,
  pairing_text,
  tokenize='unicode61 remove_diacritics 1',
  prefix='2,3,4'
)
/* dishes_fts(name,description,dish_type,pairing_text) */;
CREATE TABLE IF NOT EXISTS 'dishes_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'dishes_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'dishes_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3);
CREATE TABLE IF NOT EXISTS 'dishes_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'dishes_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS "users" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "email" varchar DEFAULT '' NOT NULL, "encrypted_password" varchar DEFAULT '' NOT NULL, "reset_password_token" varchar, "reset_password_sent_at" datetime(6), "remember_created_at" datetime(6), "created_at" datetime(6) NOT NULL, "updated_at" datetime(6) NOT NULL, "eating_profile" text /*application='Macedo'*/);
CREATE UNIQUE INDEX "index_users_on_email" ON "users" ("email") /*application='Macedo'*/;
CREATE UNIQUE INDEX "index_users_on_reset_password_token" ON "users" ("reset_password_token") /*application='Macedo'*/;
CREATE TABLE IF NOT EXISTS "dishes" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "name" varchar, "description" text, "dish_type" varchar, "favorite" boolean, "user_notes" text, "created_at" datetime(6) NOT NULL, "updated_at" datetime(6) NOT NULL, "pairing_suggestions" json DEFAULT '[]', "user_id" integer, CONSTRAINT "fk_rails_9511618633"
FOREIGN KEY ("user_id")
  REFERENCES "users" ("id")
);
CREATE INDEX "index_dishes_on_user_id" ON "dishes" ("user_id") /*application='Macedo'*/;
INSERT INTO "schema_migrations" (version) VALUES
('20251004175831'),
('20251004164908'),
('20251004164858'),
('20251004162535'),
('20251004144749'),
('20251004134435'),
('20251004134412'),
('20251004134358');

