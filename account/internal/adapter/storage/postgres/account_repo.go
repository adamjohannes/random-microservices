package postgres

import (
	"account/internal/domain"
	"context"
	"errors"
	"time"

	"gorm.io/gorm"
)

// GORM DTO
type accountDBModel struct {
	ID           string         `gorm:"primaryKey;type:uuid"`
	Email        string         `gorm:"unique;not null"`
	PasswordHash string         `gorm:"not null"`
	Name         string         `gorm:"not null"`
	CreatedAt    time.Time      `gorm:"autoCreateTime"`
	UpdatedAt    time.Time      `gorm:"autoUpdateTime"`
	DeletedAt    gorm.DeletedAt `gorm:"index"`
}

func toDBModel(account *domain.Account) accountDBModel {
	return accountDBModel{
		ID:           account.ID.String(),
		Email:        account.Email.String(),
		PasswordHash: account.Password.Hash(),
		Name:         account.Name.String(),
		CreatedAt:    account.CreatedAt,
		UpdatedAt:    account.UpdatedAt,
	}
}

func toDomainModel(db accountDBModel) (*domain.Account, error) {
	accountID, err := domain.BuildAccountID(db.ID)
	if err != nil {
		return nil, err
	}

	var deletedAt *time.Time
	if db.DeletedAt.Valid {
		deletedAt = &db.DeletedAt.Time
	}

	return domain.BuildAccount(
		accountID,
		db.Email,
		db.PasswordHash,
		db.Name,
		db.CreatedAt,
		db.UpdatedAt,
		deletedAt,
	), nil
}

type AccountRepository struct {
	db *gorm.DB
}

func NewAccountRepository(db *gorm.DB) *AccountRepository {
	return &AccountRepository{db: db}
}

// Migrate runs the database migrations.
func Migrate(db *gorm.DB) error {
	return db.AutoMigrate(&accountDBModel{})
}

// Create adds a new Account entry in the database.
func (r *AccountRepository) Create(ctx context.Context, account *domain.Account) error {
	dbModel := toDBModel(account)
	err := r.db.WithContext(ctx).Create(&dbModel).Error
	if errors.Is(err, gorm.ErrDuplicatedKey) {
		return domain.ErrEmailTaken
	}

	return err
}

// GetByID returns an Account entry from the database by ID.
func (r *AccountRepository) GetByID(ctx context.Context, id domain.AccountID) (*domain.Account, error) {
	var dbModel accountDBModel

	err := r.db.WithContext(ctx).First(&dbModel, "id = ?", id.String()).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, domain.ErrAccountNotFound
		}
		return nil, err
	}

	return toDomainModel(dbModel)
}

// GetByEmail returns an Account entry from the database by e-mail address.
func (r *AccountRepository) GetByEmail(ctx context.Context, address string) (*domain.Account, error) {
	var dbModel accountDBModel

	err := r.db.WithContext(ctx).First(&dbModel, "email = ?", address).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, domain.ErrAccountNotFound
		}
		return nil, err
	}

	return toDomainModel(dbModel)
}

// Update saves modifications to an existing Account.
func (r *AccountRepository) Update(ctx context.Context, account *domain.Account) error {
	dbModel := toDBModel(account)
	return r.db.WithContext(ctx).Save(&dbModel).Error
}

// SoftDelete marks an account as deleted. Doesn't actually remove any entries from the database.
func (r *AccountRepository) SoftDelete(ctx context.Context, id domain.AccountID) error {
	return r.db.WithContext(ctx).Delete(&accountDBModel{}, "id = ?", id.String()).Error
}
