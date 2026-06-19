# B3 — Test Discovery (Library Management API)

**Task:** B3 — Test Discovery  
**Reference files:** `beginner/B3-test-discovery/README.md`, `beginner/B3-test-discovery/TEST_REPORT.md`  
**Project:** Library Management System / `library-management`  
**API base:** http://127.0.0.1:8081  
**Note:** Port 8081 used because 8080 was occupied by another Java process.

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Test framework | **JUnit 5** / Spring Boot Test (Maven) |
| Test command | `./mvnw test` |
| Test source files | **1** |
| Tests run | **1** |
| Tests passed | **1** |
| Tests failed | **0** |
| **Result** | **PASS** |

Frameworks **not** present: pytest, Jest, Cargo (this is a Java/Spring Boot project).

---

## Test framework discovery

| Framework | Found | Location |
|-----------|-------|----------|
| JUnit 5 | Yes | `src/test/java/com/library/management/LibraryManagementApplicationTests.java` |
| Spring Boot Test | Yes | `@SpringBootTest` |
| pytest | No | — |
| Jest | No | — |
| Cargo | No | — |

### Test file

| File | Framework | Test |
|------|-----------|------|
| `LibraryManagementApplicationTests.java` | JUnit 5 | `contextLoads()` |

---

## Library Management API endpoints

| Method | Path | Controller |
|--------|------|------------|
| GET | `/api/v1/books` | BookController |
| GET | `/api/v1/books/{id}` | BookController |
| GET | `/api/v1/books/search` | BookController |
| POST | `/api/v1/books` | BookController |
| PUT | `/api/v1/books/{id}` | BookController |
| GET | `/api/v1/authors` | AuthorController |
| GET | `/api/v1/authors/{id}` | AuthorController |
| POST | `/api/v1/authors` | AuthorController |
| PUT | `/api/v1/authors/{id}` | AuthorController |
| POST | `/api/v1/members` | MemberController |
| GET | `/api/v1/members/{id}` | MemberController |
| GET | `/api/v1/members/{id}/borrows` | MemberController |
| POST | `/api/v1/borrows` | BorrowController |
| GET | `/api/v1/borrows/overdue` | BorrowController |

### Live verification

```bash
curl http://127.0.0.1:8081/api/v1/books
curl http://127.0.0.1:8081/api/v1/authors
```

Both returned **HTTP 200** on 2026-06-18.

---

## Execution log

```text
Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
-- in com.library.management.LibraryManagementApplicationTests
```

Command: `./mvnw test` from `library-management/`  
Exit code: **0**

---

## Verification summary

| Metric | Value |
|--------|------:|
| Framework | JUnit 5 / Maven |
| Tests run | 1 |
| Pass rate | 100% |
| API endpoints verified | GET /api/v1/books, GET /api/v1/authors |
| **Overall result** | **PASS** |
