import {GET_ME_FAIL, GET_ME_SUCCESS, GET_ME_REQUEST} from "./types";
import axios from "axios";

export const getMe = (token) => async dispatch => {
    const config = {
        params: {
            token: token
        }
    }

    if (!config.params.token) {
        dispatch({
            type: GET_ME_FAIL
        });
        return;
    }

    dispatch({
        type: GET_ME_REQUEST
    });

    try {
        const res = await axios.get(`${process.env.REACT_APP_DTASKBOT_API_URL}/users`, config)
        if (res.status === 200) {
            dispatch({
                type: GET_ME_SUCCESS,
                payload: res.data
            })
        } else {
            dispatch({
                type: GET_ME_FAIL
            });
        }
    } catch (err) {
        console.log(`ERROR WHILE GETTING ME ${err}`)
        if (err.response && err.response.status === 401) {
            // TODO: handle 401
        }
        dispatch({
            type: GET_ME_FAIL
        });
    }
}