import {Link, useParams, useSearchParams} from "react-router-dom";
import {getOffers} from "../actions/offers";
import {connect} from "react-redux";
import {useEffect} from "react";
import {Oval} from "react-loader-spinner";
import {Descriptions, Skeleton, Tag, Typography} from "antd";
import {Avatar} from "antd";
import {UserOutlined} from '@ant-design/icons';
import {Tabs} from "antd";
import '../styles/OfferPage.css'

const getTimeStamp = (date1, date2) => {
    const diff = Math.abs(date1-date2);
    if (Math.floor(diff / (1000 * 3600 * 24)) > 0) {
        return `${Math.floor(diff / (1000 * 3600 * 24))} дней`;
    } else if (Math.floor(diff / (1000 * 3600)) > 0) {
        return `${Math.floor(diff / (1000 * 3600))} часов`
    } else if (Math.floor(diff / (1000 * 60)) > 0) {
        return `${Math.floor(diff / (1000 * 60))} минут`
    } else {
        return `${Math.floor(diff / 1000)} секунд`
    }
}

const getOfferParams = (offer) => {
    return [
        {
            key: 'budget',
            label: 'Предложенный бюджет',
            children: `${offer.budget}₽`
        },
        {
            key: 'deadline_days',
            label: 'Предложенный срок',
            children: `${offer.deadline_days} дней`
        },
        {
            key: 'created_at',
            label: 'Отклик отправлен',
            children: offer.created_at.split('.')[0].split('T').join(' ')
        },
        {
            label: 'Скорость отклика',
            children: getTimeStamp(Date.parse(offer.created_at.replace('T', ' ').replace('Z', '')), Date.parse(offer.task.created_at.replace('T', ' ').replace('Z', '')))
        }
    ]
}

const getOfferDescription = (offer) => {
    return [
        {
            key: 'description',
            label: 'Описание',
            children: offer.description
        }
    ]
}

const getOfferTab = (offer) => {
    const offerDescription = getOfferDescription(offer);
    const offerParams = getOfferParams(offer);
    return (
        <div>
            <Descriptions items={offerDescription} title={'Подробнее об отклике'} layout={'vertical'} column={1}/>
            <Descriptions items={offerParams} layout={'horizontal'}/>
        </div>
    )
}

const getFreelancerAccountInfo = (freelancer) => {
    const paymentTypes = {
        SBER: 'Сбер',
        SELF_EMPLOYED: 'Самозанятость',
        CRYPTO: 'Крипта',
        NONCASH: 'Безнал'
    }
    const juridicalTypes = {
        SELF_EMPLOYED: 'Самозанятый',
        IP: 'ИП',
        OOO: 'ООО',
        PHYSICAL: 'Физлицо'
    }

    return [
        {
            label: 'Дата регистрации',
            children: freelancer.registered_at.split('T')[0]
        },
        {
            label: 'Выполнено заказов',
            children: freelancer.completed_tasks_count
        },
        {
            label: 'Дней в сервисе',
            children: freelancer.days_in_service
        },
        {
            label: 'Юр. статус',
            children: juridicalTypes[freelancer.juridical_type]
        },
        {
            label: 'Способы оплаты',
            children: freelancer.payment_types.map(p => paymentTypes[p]).join(', '),
        }
    ]
}

const getFreelancerTab = (freelancer) => {
    const accountInfo = getFreelancerAccountInfo(freelancer)
    return (
        <div>
            <div className={'freelancer-general'}>
                <Avatar size={64} icon={<UserOutlined/>}/>
                <div className={'freelancer-contact'}>
                    <Typography.Text className={'full-name'} strong>{freelancer.full_name}</Typography.Text>
                    <br/>
                    {freelancer.username != null ? <a className={'freelancer-username'} href={`https://t.me/${freelancer.username}`} target={'_blank'}>@{freelancer.username}</a> : null}
                    <p className={'freelancer-phone'}>{freelancer.phone.startsWith('+') ? freelancer.phone : '+' + freelancer.phone}</p>
                </div>
            </div>
            <Descriptions title={'О себе'} items={[{children: freelancer.bio}]}/>
            <Descriptions
                title={'Навыки'}
                items={[{children: freelancer.skills.map((s) => <Tag>{s}</Tag>)}]}
            />
            <Descriptions items={accountInfo}/>
        </div>
    )
}

function OfferPage ({ getOffers, offers}) {
    const p = useParams();
    const [searchParams, setSearchParams] = useSearchParams();

    useEffect(() => {
        const fetchOffers = async () => {
            await getOffers(searchParams);
        }
        if (offers === null || offers.find(o => o.id === parseInt(p.id)) === undefined) {
            // console.log(offers.find(o => o.id === p.id))
            fetchOffers();
        }
    });

    if (offers === null || offers.find(o => o.id === parseInt(p.id)) === undefined) {
        return <Skeleton active/>
    }

    const offer = offers.find(o => o.id === parseInt(p.id))
    const offerTab = getOfferTab(offer);
    const freelancerTab = getFreelancerTab(offer.author)
    const tabItems = [
        {
            key: 'offer',
            label: 'Отклик',
            children: offerTab
        },
        {
            key: 'freelancer',
            label: 'Об исполнителе',
            children: freelancerTab
        }
    ]

    return (
        <div>
            <Typography.Title level={3}>
                {'Отклик на задачу '}
                <Link to={`/tasks/?token=${searchParams.get('token')}&task_id=${offer.task.id}`}>
                    {offer.task.title}
                </Link>
            </Typography.Title>
            <Tabs items={tabItems} defaultActiveKey={'offer'}/>
        </div>
    )
}

const mapStateToProps = state => ({
    offers: state.offers.offers
});

export default connect(mapStateToProps, {getOffers})(OfferPage);