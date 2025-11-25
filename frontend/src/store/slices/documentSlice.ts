/**
 * Document Redux Slice
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../../utils/apiClient';

interface DocumentState {
  documents: any[];
  currentDocument: any;
  sections: any[];
  generatedContent: any[];
  isLoading: boolean;
  error: string | null;
}

const initialState: DocumentState = {
  documents: [],
  currentDocument: null,
  sections: [],
  generatedContent: [],
  isLoading: false,
  error: null,
};

export const fetchDocument = createAsyncThunk(
  'documents/fetchDocument',
  async (documentId: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(`/documents/${documentId}`);
      return response.data.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch document');
    }
  }
);

const documentSlice = createSlice({
  name: 'documents',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDocument.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchDocument.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentDocument = action.payload;
        state.sections = action.payload.sections || [];
      })
      .addCase(fetchDocument.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export default documentSlice.reducer;
