This is a [Next.js](https://nextjs.org/) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/basic-features/font-optimization) to automatically optimize and load Inter, a custom Google Font.

## Getting Started (Python Setup)
This section provides guidance on configuring this project on your local machine and running the Streamlit application locally.
### Prerequisites
To run this project, ensure that your PC/Laptop has the following prerequisites:
- Python
- Integrated Development Environment (IDE) such as PyCharm or Visual Studio Code.

### Project Setup

To initialize this project on your local machine, kindly adhere to the outlined instructions provided herewith. By following these meticulously crafted steps, you will seamlessly configure the project environment for optimal functionality on your personal workstation. Your cooperation in adhering to these guidelines is greatly appreciated.

1. Create a new virtual environment by using the command
   ```sh
   python -m venv .venv
   ```
2. Activate the newly created virtual environment
   ```sh
   .venv\Scripts\activate.bat
   ```
3. Install all the required project dependencies by executing the provided command. Subsequent to running this command, the internal setup file will be invoked, facilitating the configuration of your project by identifying and installing the necessary packages.
   ```sh
   pip install -r requirements.txt
   ```
4. After successfully installing all essential dependencies, proceed to run Streamlit locally by executing the following command:
   ```sh
   fastapi dev Home.py


## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js/) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/deployment) for more details.
