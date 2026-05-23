import { render, screen, waitFor } from "@testing-library/react";
import App from "./App";

beforeEach(() => {
  global.fetch = jest.fn((url) => {
    if (String(url).includes("/health")) {
      return Promise.resolve({
        json: () => Promise.resolve({ llm_connected: true, rag_engine: "langchain" }),
      });
    }

    if (String(url).includes("/engine")) {
      return Promise.resolve({
        json: () => Promise.resolve({ engine: "langchain" }),
      });
    }

    if (String(url).includes("/documents")) {
      return Promise.resolve({
        json: () => Promise.resolve([]),
      });
    }

    return Promise.resolve({ json: () => Promise.resolve({}) });
  });
});

afterEach(() => {
  jest.resetAllMocks();
});

test("renders app shell", async () => {
  render(<App />);
  expect(screen.getByText(/RAG Studio Pro/i)).toBeInTheDocument();
  expect(screen.getByText(/Portfolio SaaS Intelligence Layer/i)).toBeInTheDocument();
  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalled();
  });
});
