import rootReducer from './reducers';
import {configureStore} from "@reduxjs/toolkit";
export default configureStore({
    reducer: rootReducer
});