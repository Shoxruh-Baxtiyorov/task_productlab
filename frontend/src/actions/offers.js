import {
    OFFERS_FETCH_SUCCESS,
    OFFERS_FETCH_FAIL,
    OFFER_REJECT_FAIL,
    OFFER_REJECT_SUCCESS,
    OFFER_ACCEPT_FAIL, OFFER_ACCEPT_SUCCESS
} from "./types";
import axios from "axios";

export const acceptOffer = (offer, qparams) => async dispatch => {
    const config = {
        params: {
            token: qparams.get('token')
        }
    }

    if (config.params.token === null) {
        // TODO: DO something with 401
        dispatch({
            type: OFFER_ACCEPT_FAIL
        })
    }

    try {
        const res = await axios.post(`${process.env.REACT_APP_DTASKBOT_API_URL}/offers/client/${offer.id}/accept`, null, config)

        if (res.status === 200) {
            dispatch({
                type: OFFER_ACCEPT_SUCCESS,
                payload: {offerId: offer.id}
            });
        } else {
            console.log(`CANNOT ACCEPT OFFER ${res.status}`)
            dispatch({
                type: OFFER_ACCEPT_FAIL
            })
        }
    } catch (err) {
        console.log(`FAIL WHILE ACCEPTING OFFER ${err}`)
        if (err.response.status === 401) {
            // TODO: handle 401
        }
        dispatch({
            type: OFFER_ACCEPT_FAIL
        })
    }
}

export const rejectOffer = (offer, qparams) => async dispatch => {
    const config = {
        params: {
            token: qparams.get('token'),
            status: 'REJECTED'
        }
    }

    if (config.params.token === null) {
        // TODO: 401
        dispatch({
            type: OFFER_REJECT_FAIL
        });
    }

    try {
        const res = await axios.post(`${process.env.REACT_APP_DTASKBOT_API_URL}/offers/client/${offer.id}/status`, null, config)

        if (res.status === 200) {
            dispatch({
                type: OFFER_REJECT_SUCCESS,
                payload: {offerId: offer.id, data: res.data}
            });
        } else {
            console.log(`CANNOT REJECT OFFER. STATUS: ${res.status}`)
            dispatch({
                type: OFFER_REJECT_FAIL
            });
        }
    } catch (err) {
        console.log(`ERROR WHILE FETCHING OFFERS ${err}`)
        if (err.response.status === 401) {
            // TODO: handle 401
        }
        dispatch({
            type: OFFER_REJECT_FAIL
        });
    }
}

export const getOffers = (qparams) => async dispatch => {
    const config = {
        params: {
            token: qparams.get('token'),
            task_id: qparams.get('task_id'),
            offset: qparams.get('offset'),
            limit: qparams.get('limit')
        }
    }

    if (config.params.token === null) {
        // TODO: unauthorized
        dispatch({
            type: OFFERS_FETCH_FAIL
        });
    }

    try {
        const res = await axios.get(`${process.env.REACT_APP_DTASKBOT_API_URL}/offers/client`, config)

        if (res.status === 200) {
            dispatch({
                type: OFFERS_FETCH_SUCCESS,
                payload: res.data
            });
        } else {
            console.log(`CANNOT FETCH OFFERS. STATUS: ${res.status}`)
            dispatch({
                type: OFFERS_FETCH_FAIL
            });
        }
    } catch (err) {
        console.log(`ERROR WHILE FETCHING OFFERS ${err}`)
        if (err.response.status === 401) {
            // TODO: handle 401
        }
        dispatch({
            type: OFFERS_FETCH_FAIL
        });
    }
}