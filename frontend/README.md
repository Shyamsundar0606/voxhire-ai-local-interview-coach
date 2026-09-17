This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

 # VoxHire AI Frontend

 Next.js App Router frontend foundation for VoxHire AI. Milestone 1 provides a responsive dark dashboard shell, navigation sidebar, typed API client, and backend health loading/error states.

 ## Requirements

 - Node.js LTS
 - npm
 - FastAPI backend running at the URL configured by `NEXT_PUBLIC_API_URL`

 ## Setup

 ```powershell
 Copy-Item .env.example .env.local
 npm install
 ```

 ## Run

 ```powershell
 npm run dev
 ```

 Open `http://localhost:3000`.

 ## Quality Checks

 ```powershell
 npm run lint
 npm run type-check
 npm run build
 ```

 Authentication, AI integrations, resume processing, speech processing, and interview workflows are intentionally not included in Milestone 1.
