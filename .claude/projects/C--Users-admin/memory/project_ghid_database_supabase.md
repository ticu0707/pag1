---
name: project_ghid_database_supabase
description: "Ghid Database Design & Supabase/PostgreSQL pentru vibe-coding (17 secțiuni, 5 Blocuri + Realtime + Presence): normalizare, tipuri, relații, RLS, indexare, views, funcții, transactions, migrations, TypeScript types"
metadata: 
  node_type: memory
  type: project
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Ghid Skill 5 — Database Design & Supabase/PostgreSQL v2.0 COMPLET, salvat la Desktop/Vibe-Coding/ghid-database-supabase-v2.md

**Why:** Cel mai scump tip de greșeală — schema proastă se corectează greu după date reale. FinanceOS, ERP, Clinică și StudioFlow au scheme complexe (RLS, foreign keys, views, funcții atomice).

**How to apply:** Referință la orice sesiune cu Supabase — în special pentru RLS (Parte 6-7), tipuri PostgreSQL (Parte 1), relații (Parte 2), transactions (Parte 11), checklist pre-deploy (Parte 15).

## Structură

17 secțiuni (0–16) în 5 Blocuri:
- Bloc 1: Schema Design (normalizare 1NF/2NF/3NF, tipuri PG, relații 1:1/1:N/N:N)
- Bloc 2: Supabase JS (SELECT/JOIN, INSERT/UPDATE/DELETE, filtre/paginare)
- Bloc 3: Securitate și Performanță (RLS, policies, indexare)
- Bloc 4: Operații complexe (views, funcții RPC, triggers, transactions, migrations)
- Bloc 5: Debugging și Toolkit (8 greșeli comune, TypeScript types, checklist, Quick Reference Card)

## Appendix: Schema Template Starter

Include SQL complet gata de copiat pentru orice proiect Supabase cu:
- Profil utilizator legat de auth.users (1:1)
- Trigger auto updated_at
- Trigger handle_new_user la signup
- Tabelă invoices cu RLS complet (SELECT/INSERT/UPDATE/DELETE policies)
- Indexuri pe foreign keys și câmpuri filtrate frecvent

## Fix-uri v1.1 (rafinări expert)
- FOR UPDATE în transfer_funds (race condition financiară)
- CREATE INDEX CONCURRENTLY (downtime producție)
- SECURITY DEFINER + SET search_path = public, auth (SQL injection prin schema)
- Policy admin via JWT app_metadata, nu subquery la profiles (recursivitate)
- Sintaxa N:N corectă + soft delete + N+1 + FOR UPDATE SKIP LOCKED + auth.role()

## Fix-uri v2.0 (a doua rundă rafinare expert exhaustivă)
- FIX REGRESIE: `COALESCE(full_name, '')` → NULL în Appendix (era rămas din v1.1)
- ADĂUGAT: `FORCE ROW LEVEL SECURITY` — owner bypass RLS implicit (Parte 6)
- ADĂUGAT: `citext` extension + Domain types (Parte 1)
- ADĂUGAT: UPSERT cu `onConflict` explicit + `.throwOnError()` (Parte 4)
- ADĂUGAT: `.or()`, `.contains()/.overlaps()`, `.textSearch()` (Parte 5)
- ADĂUGAT: Cursor-based pagination (Parte 5)
- ADĂUGAT: `count: 'estimated'` vs `count: 'exact'` (Parte 3 + Greșeala 13)
- ADĂUGAT: BRIN index + Covering index INCLUDE + index bloat monitoring (Parte 8)
- ADĂUGAT: Supabase Cron pentru materialized view refresh (Parte 9)
- ADĂUGAT: Function volatility STABLE/IMMUTABLE/VOLATILE + STRICT (Parte 10)
- ADĂUGAT: RETURNS TABLE pattern (Parte 10)
- ADĂUGAT: Isolation levels REPEATABLE READ/SERIALIZABLE (Parte 11)
- ADĂUGAT: Deadlock prevention — ordine deterministă lock-uri (Parte 11)
- ADĂUGAT: SAVEPOINT pentru rollback parțial (Parte 11)
- ADĂUGAT: `supabase db reset` warning + down migrations strategy (Parte 12)
- ADĂUGAT: Column type change cu USING clause (Parte 12)
- ADĂUGAT: Greșeala 13 — count exact performanță
- ADĂUGAT: `createClient<Database>` typed client + `satisfies` operator (Parte 14)
- ADĂUGAT: Subscribe error handling + Presence/Broadcast API (Parte 16)
- ACTUALIZAT: Appendix cu FORCE RLS, index compus, version column, NULL corect
- ACTUALIZAT: Checklist + Quick Reference Card complet

[[project_erp_financiar]] [[project_clinica_medicala]] [[project_vibe_budget]] [[project_studioflow]]
