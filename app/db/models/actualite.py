from datetime import datetime
from uuid import UUID, uuid4
from app.db.models.categorie_actualite import CategorieActualite 
from sqlmodel import Field, SQLModel, Relationship
from app.db.models.user import User



class Actualite(SQLModel, table=True):
    __tablename__ = "actualites"

    uid: UUID = Field(default_factory=uuid4, primary_key=True)

    titre: str | None = Field(default=None,max_length=255,nullable=True)
    slug: str | None = Field(default=None,max_length=255,nullable=True)
        
    resume: str | None = Field(default=None, max_length=500)
    contenu: str

    image_url: str | None = Field(default=None, max_length=500)
    image_alt: str | None = Field(default=None, max_length=255)

    auteur_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        index=True,
    )

    categorie_uid: UUID | None = Field(
        default=None,
        foreign_key="categorie_actualites.uid",
        index=True,
    )
    #statut actualite: brouillon, publie ou archive
    statut: str = Field(default="brouillon", max_length=30, index=True)
    est_a_la_une: bool = Field(default=False, index=True)
    nombre_vues: int = Field(default=0, ge=0)
    
    fichier_key: str | None = Field(
        default=None,
        max_length=500,
    )

    date_publication: datetime | None = Field(default=None, index=True)
    cree_le: datetime = Field(default_factory=datetime.utcnow)
    modifie_le: datetime = Field(default_factory=datetime.utcnow)
    cree_par_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )
    modifie_par_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )
    is_deleted: bool = Field(default=False, index=True)
    supprime_le: datetime | None = None
    supprime_par_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )
    
    cree_par: User | None = Relationship(
        back_populates="actualites_crees",
        sa_relationship_kwargs={
            "foreign_keys": "[Actualite.cree_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    modifie_par: User | None = Relationship(
        back_populates="actualites_modifies",
        sa_relationship_kwargs={
            "foreign_keys": "[Actualite.modifie_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    supprime_par: User | None = Relationship(
        back_populates="actualites_supprimes",
        sa_relationship_kwargs={
            "foreign_keys": "[Actualite.supprime_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    
    categorie_actualite: CategorieActualite | None = Relationship(
        back_populates="actualites", 
        sa_relationship_kwargs={
            "foreign_keys": "[Actualite.categorie_uid]"
        }
    )
    