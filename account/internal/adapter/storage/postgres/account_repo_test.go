//go:build integration

package postgres

import (
	"account/internal/domain"
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	tcpostgres "github.com/testcontainers/testcontainers-go/modules/postgres"
	gormpostgres "gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var testDB *gorm.DB

func TestMain(m *testing.M) {
	ctx := context.Background()

	container, err := tcpostgres.Run(ctx, "postgres:17",
		tcpostgres.WithDatabase("accounts"),
		tcpostgres.WithUsername("test"),
		tcpostgres.WithPassword("test"),
		tcpostgres.BasicWaitStrategies(),
	)
	if err != nil {
		panic(err)
	}

	dsn, err := container.ConnectionString(ctx, "sslmode=disable")
	if err != nil {
		panic(err)
	}

	// TranslateError must match cmd/api/main.go for ErrEmailTaken to reproduce.
	testDB, err = gorm.Open(gormpostgres.Open(dsn), &gorm.Config{TranslateError: true})
	if err != nil {
		panic(err)
	}

	if err := Migrate(testDB); err != nil {
		panic(err)
	}

	code := m.Run()

	_ = container.Terminate(ctx)
	if code != 0 {
		panic("integration tests failed")
	}
}

func freshRepo(t *testing.T) *AccountRepository {
	t.Helper()
	require.NoError(t, testDB.Exec("TRUNCATE account_db_models").Error)
	return NewAccountRepository(testDB)
}

func newAccount(t *testing.T, email string) *domain.Account {
	t.Helper()
	account, err := domain.NewAccount(email, "StrongPass1!", "John Doe")
	require.NoError(t, err)
	return account
}

func TestCreateAndGetByID(t *testing.T) {
	repo := freshRepo(t)
	ctx := context.Background()
	account := newAccount(t, "getbyid@example.com")

	require.NoError(t, repo.Create(ctx, account))

	got, err := repo.GetByID(ctx, account.ID)
	require.NoError(t, err)
	assert.Equal(t, account.ID.String(), got.ID.String())
	assert.Equal(t, account.Email.String(), got.Email.String())
	assert.Equal(t, account.Name.String(), got.Name.String())
	assert.True(t, got.Password.Compare("StrongPass1!"))
	assert.False(t, got.CreatedAt.IsZero())
}

func TestCreateAndGetByEmail(t *testing.T) {
	repo := freshRepo(t)
	ctx := context.Background()
	account := newAccount(t, "getbyemail@example.com")

	require.NoError(t, repo.Create(ctx, account))

	got, err := repo.GetByEmail(ctx, "getbyemail@example.com")
	require.NoError(t, err)
	assert.Equal(t, account.ID.String(), got.ID.String())
}

func TestCreateDuplicateEmail(t *testing.T) {
	repo := freshRepo(t)
	ctx := context.Background()

	require.NoError(t, repo.Create(ctx, newAccount(t, "dup@example.com")))

	err := repo.Create(ctx, newAccount(t, "dup@example.com"))
	assert.ErrorIs(t, err, domain.ErrEmailTaken)
}

func TestGetByIDNotFound(t *testing.T) {
	repo := freshRepo(t)

	_, err := repo.GetByID(context.Background(), domain.NewAccountID())
	assert.ErrorIs(t, err, domain.ErrAccountNotFound)
}

func TestGetByEmailNotFound(t *testing.T) {
	repo := freshRepo(t)

	_, err := repo.GetByEmail(context.Background(), "missing@example.com")
	assert.ErrorIs(t, err, domain.ErrAccountNotFound)
}

func TestUpdatePersists(t *testing.T) {
	repo := freshRepo(t)
	ctx := context.Background()
	account := newAccount(t, "update@example.com")
	require.NoError(t, repo.Create(ctx, account))

	require.NoError(t, account.UpdateName("Jane Doe"))
	require.NoError(t, account.UpdateEmail("updated@example.com"))
	require.NoError(t, repo.Update(ctx, account))

	got, err := repo.GetByID(ctx, account.ID)
	require.NoError(t, err)
	assert.Equal(t, "Jane Doe", got.Name.String())
	assert.Equal(t, "updated@example.com", got.Email.String())
}

func TestSoftDelete(t *testing.T) {
	repo := freshRepo(t)
	ctx := context.Background()
	account := newAccount(t, "delete@example.com")
	require.NoError(t, repo.Create(ctx, account))

	require.NoError(t, repo.SoftDelete(ctx, account.ID))

	_, err := repo.GetByID(ctx, account.ID)
	assert.ErrorIs(t, err, domain.ErrAccountNotFound)
}
