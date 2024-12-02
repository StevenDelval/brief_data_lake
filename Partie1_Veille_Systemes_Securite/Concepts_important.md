# Les concepts importants

## 1. Storage Access Keys

Les Storage Access Keys dans Azure sont des clés secrètes utilisées pour authentifier l'accès à un compte de stockage Azure. Elles permettent aux utilisateurs ou applications d'accéder directement aux ressources d'un compte de stockage, comme les conteneurs, les fichiers ou les Data Lakes, sans passer par Azure Active Directory (Azure AD / Microsoft Entra ID).

Chaque compte de stockage Azure est associé à deux clés d'accès (primaire et secondaire).
Ces clés sont interchangeables pour permettre une rotation des clés (bonne pratique pour renforcer la sécurité).

Une Storage Access Key donne un accès complet au compte de stockage.
Cela inclut la possibilité de lire, écrire, supprimer ou modifier toutes les données.

### Avantages des Storage Access Keys

- Simplicité : Utiliser les clés est simple et rapide, sans configuration préalable d’identité.
- Continuité des opérations : Les deux clés permettent une rotation sécurisée sans interrompre l'accès aux données.

### Inconvénients et limitations

- Manque de granularité :
        Les Storage Access Keys ne permettent pas de limiter l'accès à certaines actions ou ressources spécifiques.
        Toute personne ou application possédant une clé peut manipuler l’ensemble des données du compte.

- Risque de compromission :
        Si une clé est exposée (par exemple, dans un script ou une application), l'accès aux données devient vulnérable.
        Aucun mécanisme natif pour limiter l'accès géographiquement ou en fonction de l’appareil.


## 2. Shared Access Signatures (SAS) (Delegation Key)
Les Shared Access Signatures (SAS) sont un mécanisme permettant de déléguer temporairement l'accès à des ressources spécifiques dans un compte de stockage Azure, comme des blobs, fichiers, ou conteneurs.

Contrairement aux Storage Access Keys, les SAS offrent un contrôle beaucoup plus précis en limitant :

- Les actions autorisées (lecture, écriture, suppression, etc.).
- La durée de validité.
- La ressource spécifique concernée.

### Avantages des SAS

- Granularité des permissions :
        Les permissions peuvent être adaptées à différents scénarios (partage public, collaboration, etc.).
    - Exemple : lecture seule, écriture seule, ou modification sur un fichier spécifique.

- Durée limitée :
        Les SAS ont une période d'expiration clairement définie.
        Après cette durée, le jeton SAS devient inutile, ce qui réduit le risque de compromission à long terme.

- Pas de besoin de clés d'accès exposées :
        Les utilisateurs ou applications n’ont pas besoin d’accéder aux Storage Access Keys directement.

## 3. Microsoft Entra ID (anciennement Azure Active Directory) (service principal)
Microsoft Entra ID est le nouveau nom donné à Azure Active Directory (Azure AD).
Microsoft Entra ID est un service cloud de gestion des identités et des accès. Il permet aux organisations de :
- Authentifier et autoriser les utilisateurs, les applications et les services.
- Contrôler qui peut accéder à quelles ressources en appliquant des règles de sécurité spécifiques.

## 4. Azure Key Vault
Azure Key Vault est un service cloud de Microsoft Azure conçu pour sécuriser et gérer les secrets, clés de chiffrement et certificats utilisés par les applications, services et utilisateurs. Il joue un rôle clé dans la sécurité des données en permettant de centraliser et de protéger les informations sensibles.

## 5. IAM
IAM (Identity and Access Management) est un ensemble de pratiques, technologies et systèmes permettant de gérer les identités numériques et de contrôler leur accès aux ressources d’un système informatique. Dans le contexte d’Azure, IAM désigne principalement les fonctionnalités liées aux mécanismes de contrôle des accès pour sécuriser les données, applications, et infrastructures.

## 6. Role-Based Access Control (RBAC)
Role-Based Access Control (RBAC) est un système de gestion des permissions qui permet de contrôler l’accès aux ressources en fonction des rôles attribués aux utilisateurs, groupes, ou applications. Azure RBAC est une solution native dans Microsoft Azure pour implémenter un contrôle d’accès granulaire et basé sur les rôles, en s’intégrant à Azure Active Directory (Azure AD).