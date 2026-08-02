# 🐶 PetGo Backend API Guide & Testing Manual

Welcome to the **PetGo Backend API Guide**. This document covers the architecture, purpose, workflows, and testing instructions for all API modules available in the PetGo backend.

---

## 🛠️ How to Test APIs (Step-by-Step)

The easiest way to test all backend APIs without installing extra tools is using the built-in **Swagger Interactive UI**.

### Step 1: Open Swagger UI
1. Ensure your backend server is running (`python manage.py runserver`).
2. Open your browser and navigate to:
   👉 **[http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)**

### Step 2: Authenticate (Get JWT Bearer Token)
1. In Swagger UI, expand the **`POST /api/auth/login`** endpoint.
2. Click **Try it out**.
3. Pass your admin credentials:
   ```json
   {
     "username": "admin",
     "password": "adminpassword123"
   }
   ```
4. Click **Execute**.
5. Copy the returned `access` token string.

### Step 3: Authorize Swagger UI
1. Click the **Authorize 🔓** button at the top right of the Swagger page.
2. In the `Value` input field, enter:
   `Bearer YOUR_COPIED_ACCESS_TOKEN`
3. Click **Authorize** and close the modal. Now all requests executed in Swagger will carry your JWT token automatically!

---

## 🧭 Module Breakdown (Title, Purpose & User Flows)

---

### 1. 🔐 Authentication & User Module (`/api/auth/*` & `/api/user/*`)

- **Purpose:** Handles user sign-up, phone OTP verification, Google Social Auth, JWT token generation, user profiles, and delivery address management.
- **User Flow:**
  ```mermaid
  graph TD
      A[Register Request /api/auth/register] --> B[Receive OTP]
      B --> C[Verify OTP /api/auth/verify-otp]
      C --> D[Receive JWT Tokens]
      D --> E[Access Profile /api/user/profile]
      D --> F[Add Address /api/user/address]
  ```

#### Key Endpoints:
- `POST /api/auth/register` - Initiate registration & send OTP.
- `POST /api/auth/verify-otp` - Verify phone OTP & return access/refresh tokens.
- `POST /api/auth/login` - Standard email/password login.
- `GET /api/user/profile` - Retrieve logged-in user profile.
- `GET/POST /api/user/address` - Manage user shipping/billing addresses.

---

### 2. 🏥 Vet Finder Module (`/api/vet-finder/*`)

- **Purpose:** Enables pet owners to discover nearby veterinary hospitals and doctors, view hospital tags/specialties, submit ratings/reviews, and book appointments.
- **User Flow:**
  ```mermaid
  graph TD
      A[Browse Vet Hospitals /api/vet-finder/hospitals] --> B[Filter by Specialty Tags]
      B --> C[View Details & Reviews /api/vet-finder/reviews]
      C --> D[Book Appointment /api/vet-finder/appointments]
  ```

#### Key Endpoints:
- `GET /api/vet-finder/hospitals` - Search & filter veterinary clinics.
- `POST /api/vet-finder/appointments` - Book appointment with a clinic.
- `GET/POST /api/vet-finder/reviews` - View and submit hospital reviews.

---

### 3. 🏡 Foster House Finder Module (`/api/foster-house-finder/*`)

- **Purpose:** Allows pet owners to find safe temporary foster boarding houses for their pets when traveling or away.
- **User Flow:**
  ```mermaid
  graph TD
      A[Search Foster Houses /foster-house-finder/houses] --> B[View Amenities & Rates]
      B --> C[Book Temporary Stay /foster-house-finder/appointments]
      C --> D[Leave Review after Stay /foster-house-finder/reviews]
  ```

#### Key Endpoints:
- `GET /api/foster-house-finder/houses` - Discover foster homes.
- `POST /api/foster-house-finder/appointments` - Request a foster booking.
- `GET/POST /api/foster-house-finder/reviews` - Ratings and feedback.

---

### 4. ✂️ Training & Grooming Module (`/api/training-grooming/*`)

- **Purpose:** Service marketplace for pet spa, grooming, behavior training, and hygiene care.
- **User Flow:**
  ```mermaid
  graph TD
      A[Browse Grooming / Training Centers] --> B[Select Packages / Service Tags]
      B --> C[Book Appointment Slot]
      C --> D[Review Service]
  ```

#### Key Endpoints:
- `GET /api/training-grooming` - List service providers.
- `POST /api/training-grooming/appointments` - Reserve a grooming or training session.
- `GET/POST /api/training-grooming/reviews` - Service reviews & replies.

---

### 5. 🐾 Pet Adoption Module (`/api/pet-adoption/*`)

- **Purpose:** Facilitates pet adoption by connecting rescue pets or pets looking for new homes with verified adopters.
- **User Flow:**
  ```mermaid
  graph TD
      A[Browse Adoption Pets /api/pet-adoption] --> B[View Pet Health & Bio]
      B --> C[Submit Adoption Request]
      C --> D[Admin Approval /pet-adoption/{id}]
  ```

#### Key Endpoints:
- `GET /api/pet-adoption` - View available pets for adoption.
- `POST /api/pet-adoption` - Post a pet up for adoption.

---

### 6. 📦 Inventory Module (`/api/inventory/*`)

- **Purpose:** Manages the product catalog, categories, and brands for pet food, toys, accessories, and healthcare products.
- **User Flow:**
  ```mermaid
  graph TD
      A[List Categories /api/inventory/category] --> B[List Brands /api/inventory/brand]
      B --> C[Fetch Products /api/inventory/product]
  ```

#### Key Endpoints:
- `GET /api/inventory/category` - Retrieve pet product categories.
- `GET /api/inventory/brand` - Retrieve pet product brands.
- `GET /api/inventory/product` - Product listing & details.

---

## 💡 Recommended API Testing Sequence

When testing the backend, run tests in this logical order:

1. **Authentication:** Perform `POST /api/auth/login` to obtain access token.
2. **Authorize Swagger:** Put `Bearer <token>` in Swagger Authorize.
3. **User Profile:** Test `GET /api/user/profile`.
4. **Browse Services:** Test `GET /api/vet-finder/hospitals`, `GET /api/foster-house-finder/houses`, or `GET /api/inventory/product`.
5. **Bookings & Appointments:** Submit a `POST` request to create an appointment.
