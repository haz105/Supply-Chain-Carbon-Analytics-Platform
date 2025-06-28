"""
Increase precision for emissions columns in carbon_emissions table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240628_increase_precision_emissions_columns'
down_revision = 'fe1a0926322b'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('carbon_emissions', 'co2_kg', type_=sa.DECIMAL(18, 6), existing_type=sa.DECIMAL(10, 6), nullable=False)
    op.alter_column('carbon_emissions', 'ch4_kg', type_=sa.DECIMAL(18, 6), existing_type=sa.DECIMAL(10, 6), nullable=False)
    op.alter_column('carbon_emissions', 'n2o_kg', type_=sa.DECIMAL(18, 6), existing_type=sa.DECIMAL(10, 6), nullable=False)
    op.alter_column('carbon_emissions', 'co2_equivalent_kg', type_=sa.DECIMAL(18, 6), existing_type=sa.DECIMAL(10, 6), nullable=False)

def downgrade():
    op.alter_column('carbon_emissions', 'co2_kg', type_=sa.DECIMAL(10, 6), existing_type=sa.DECIMAL(18, 6), nullable=False)
    op.alter_column('carbon_emissions', 'ch4_kg', type_=sa.DECIMAL(10, 6), existing_type=sa.DECIMAL(18, 6), nullable=False)
    op.alter_column('carbon_emissions', 'n2o_kg', type_=sa.DECIMAL(10, 6), existing_type=sa.DECIMAL(18, 6), nullable=False)
    op.alter_column('carbon_emissions', 'co2_equivalent_kg', type_=sa.DECIMAL(10, 6), existing_type=sa.DECIMAL(18, 6), nullable=False) 