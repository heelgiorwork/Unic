// Заглушки для API
const API = {
    posts: {
        create: (data) => Promise.resolve({ id: Date.now(), ...data }),
        list: () => Promise.resolve([]),
        update: (id, data) => Promise.resolve({ id, ...data }),
        delete: (id) => Promise.resolve(),
        publish: (id) => Promise.resolve()
    },
    
    auth: {
        login: (data) => Promise.resolve({ user: { name: data.username } }),
        register: (data) => Promise.resolve({ user: data })
    }
};

window.API = API; // Делаем глобальным